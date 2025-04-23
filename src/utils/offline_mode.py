"""
Módulo para gerenciar o modo offline/online do AWS Price Calculator.

Este módulo fornece utilitários para:
1. Detectar se a conexão com a AWS está disponível
2. Alternar entre o uso de dados estáticos (offline) e a API AWS (online)
3. Implementar mecanismos de fallback para usar dados estáticos quando a API falha
4. Forçar modos específicos para fins de teste ou depuração

Uso típico:
```python
from utils.offline_mode import is_aws_online, with_fallback

# Verificar status atual
if is_aws_online():
    print("Usando API AWS em tempo real")
else:
    print("Usando dados estáticos")

# Usar decorator para implementar fallback automático
@with_fallback
def get_instance_price(instance_type, region, os):
    # Esta função tentará usar a API AWS,
    # mas cairá para dados estáticos se a API falhar
    ...
```
"""

import time
import logging
import functools
import requests
from typing import Callable, TypeVar, Any, Optional, Tuple, Dict, List

# Configuração de logging
logger = logging.getLogger(__name__)

# Timeout para requisições HTTP em segundos
DEFAULT_TIMEOUT = 5

# URL do endpoint de preços da AWS para verificar conectividade
AWS_PRICING_ENDPOINT = "https://pricing.us-east-1.amazonaws.com/"

# Variáveis de estado
_aws_online = None  # None = não verificado ainda, True/False = estado conhecido
_force_mode = None  # None = automático, True = forçar online, False = forçar offline

# Tipo genérico para decoradores de função
T = TypeVar("T")


def check_aws_connection(timeout: int = DEFAULT_TIMEOUT, max_retries: int = 2) -> bool:
    """
    Verifica se é possível conectar ao endpoint de preços da AWS.

    Args:
        timeout: Tempo limite em segundos para a requisição HTTP
        max_retries: Número máximo de tentativas se ocorrer um erro

    Returns:
        bool: True se a conexão for bem-sucedida, False caso contrário
    """
    global _aws_online

    # Se o modo estiver forçado, respeitamos isso
    if _force_mode is not None:
        _aws_online = _force_mode
        return _force_mode

    # Tenta conectar ao endpoint de preços da AWS
    retry_count = 0
    while retry_count <= max_retries:
        try:
            response = requests.get(AWS_PRICING_ENDPOINT, timeout=timeout)
            if response.status_code == 200:
                _aws_online = True
                logger.info("Conexão com AWS estabelecida com sucesso")
                return True
            else:
                logger.warning(
                    f"Falha ao conectar à AWS: código de status {response.status_code}"
                )
                retry_count += 1
                if retry_count <= max_retries:
                    time.sleep(1)  # Pequeno atraso entre tentativas
        except (requests.ConnectionError, requests.Timeout) as e:
            logger.warning(f"Erro de conexão com AWS: {str(e)}")
            retry_count += 1
            if retry_count <= max_retries:
                time.sleep(1)

    # Se chegou até aqui, não conseguiu conectar após todas as tentativas
    _aws_online = False
    logger.info("Modo offline ativado: Não foi possível conectar à AWS")
    return False


def is_aws_online() -> bool:
    """
    Retorna o status online da API AWS.
    Verifica a conexão na primeira chamada e armazena o resultado em cache.

    Returns:
        bool: True se a API AWS estiver acessível, False caso contrário
    """
    global _aws_online

    # Se o modo estiver forçado, respeitamos isso
    if _force_mode is not None:
        return _force_mode

    # Se ainda não verificamos, faz a verificação
    if _aws_online is None:
        return check_aws_connection()

    return _aws_online


def force_online_mode():
    """
    Força o sistema a operar em modo online, independente do estado real da conexão.
    Útil para testes e depuração.
    """
    global _force_mode, _aws_online
    _force_mode = True
    _aws_online = True
    logger.info("Modo online forçado ativado")


def force_offline_mode():
    """
    Força o sistema a operar em modo offline, independente do estado real da conexão.
    Útil para testes e depuração.
    """
    global _force_mode, _aws_online
    _force_mode = False
    _aws_online = False
    logger.info("Modo offline forçado ativado")


def reset_connection_state():
    """
    Redefine o estado da conexão para não verificado.
    A próxima chamada para is_aws_online() fará uma nova verificação.
    """
    global _aws_online, _force_mode
    _aws_online = None
    _force_mode = None
    logger.info("Estado da conexão redefinido")


def fallback_to_static(
    online_func: Callable[..., T], offline_func: Callable[..., T], *args, **kwargs
) -> T:
    """
    Tenta executar a função online, mas se falhar ou o sistema estiver offline,
    utiliza a função offline.

    Args:
        online_func: Função que usa a API AWS
        offline_func: Função que utiliza dados estáticos
        *args, **kwargs: Argumentos passados para ambas as funções

    Returns:
        O resultado da função executada (online ou offline)
    """
    if is_aws_online():
        try:
            return online_func(*args, **kwargs)
        except Exception as e:
            logger.warning(
                f"Falha na função online ({online_func.__name__}): {str(e)}. "
                f"Usando alternativa offline."
            )

    return offline_func(*args, **kwargs)


def with_fallback(offline_func: Optional[Callable] = None):
    """
    Decorador que implementa uma estratégia de fallback para funções que usam a API AWS.
    Se a função decorada falhar (ou se estiver em modo offline), a função offline será usada.

    Exemplo de uso:

    ```python
    @with_fallback(get_instance_price_static)
    def get_instance_price(instance_type, region):
        # implementação que usa a API AWS
        ...
    ```

    Ou se a função offline tiver o mesmo nome com sufixo '_static':

    ```python
    @with_fallback
    def get_instance_price(instance_type, region):
        # implementação que usa a API AWS
        ...

    def get_instance_price_static(instance_type, region):
        # implementação que usa dados estáticos
        ...
    ```

    Args:
        offline_func: A função offline a ser usada como fallback.
                     Se None, tentará usar uma função com o mesmo nome + '_static'

    Returns:
        Uma função decorada com lógica de fallback
    """

    def decorator(online_func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(online_func)
        def wrapper(*args, **kwargs) -> T:
            nonlocal offline_func

            # Se nenhuma função offline foi especificada, procura por uma com o mesmo nome + '_static'
            if offline_func is None:
                module = online_func.__module__
                func_name = f"{online_func.__name__}_static"

                try:
                    import importlib

                    module_obj = importlib.import_module(module)
                    offline_func = getattr(module_obj, func_name)
                except (ImportError, AttributeError):
                    logger.error(
                        f"Função offline '{func_name}' não encontrada no módulo '{module}'"
                    )
                    raise ValueError(f"Função de fallback '{func_name}' não disponível")

            return fallback_to_static(online_func, offline_func, *args, **kwargs)

        return wrapper

    # Permite usar o decorador com ou sem argumentos
    if callable(offline_func):
        func, offline_func = offline_func, None
        return decorator(func)

    return decorator


def log_mode_status():
    """
    Registra no log o status atual do modo online/offline.
    Útil para diagnóstico.
    """
    status = "ONLINE" if is_aws_online() else "OFFLINE"
    forced = " (FORÇADO)" if _force_mode is not None else ""
    logger.info(f"Status do AWS Price Calculator: {status}{forced}")
    return status
