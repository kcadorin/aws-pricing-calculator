"""
Utilitários para trabalhar com dados e serviços da AWS.

Este módulo oferece funções auxiliares para manipular dados relacionados aos serviços
da AWS, como validação de regiões, tipos de instância e outros recursos.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union

from src.static import aws_resources

logger = logging.getLogger(__name__)


def is_aws_credentials_available() -> bool:
    """
    Verifica se as credenciais da AWS estão disponíveis no ambiente.

    Returns:
        bool: True se as credenciais estiverem disponíveis, False caso contrário.
    """
    aws_access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    return bool(aws_access_key and aws_secret_key)


def load_static_data(resource_type: str) -> Dict:
    """
    Carrega dados estáticos de um arquivo JSON para uso offline.

    Args:
        resource_type: Tipo de recurso a ser carregado (ex: 'ec2_instances', 'ebs_volumes')

    Returns:
        Dict: Dados estáticos carregados ou dicionário vazio se o arquivo não existir
    """
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, "static", "data", f"{resource_type}.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            logger.warning(f"Arquivo de dados estáticos não encontrado: {file_path}")
            return {}
    except Exception as e:
        logger.error(f"Erro ao carregar dados estáticos: {e}")
        return {}


def validate_region(region: str) -> bool:
    """
    Valida se a região AWS fornecida é suportada.

    Args:
        region: Código da região AWS (ex: 'us-east-1')

    Returns:
        bool: True se a região for válida, False caso contrário
    """
    return aws_resources.is_valid_region(region)


def validate_instance_type(instance_type: str) -> bool:
    """
    Valida se o tipo de instância EC2 fornecido é suportado.

    Args:
        instance_type: Tipo de instância EC2 (ex: 't2.micro')

    Returns:
        bool: True se o tipo de instância for válido, False caso contrário
    """
    return aws_resources.is_valid_instance_type(instance_type)


def get_instance_specs(instance_type: str) -> Optional[Dict[str, Any]]:
    """
    Obtém as especificações de um tipo de instância EC2.

    Args:
        instance_type: Tipo de instância EC2 (ex: 't2.micro')

    Returns:
        Dict ou None: Especificações da instância ou None se não for encontrada
    """
    return aws_resources.get_instance_type_specs(instance_type)


def get_all_available_instance_types() -> List[str]:
    """
    Obtém todos os tipos de instância EC2 disponíveis.

    Returns:
        List: Lista de tipos de instância disponíveis
    """
    return aws_resources.get_all_instance_types()


def get_ec2_price_static(
    instance_type: str, region: str, operating_system: str = "Linux"
) -> float:
    """
    Obtém o preço estático de uma instância EC2 por hora.

    Args:
        instance_type: Tipo de instância EC2 (ex: 't2.micro')
        region: Região AWS (ex: 'us-east-1')
        operating_system: Sistema operacional ("Linux" ou "Windows")

    Returns:
        float: Preço por hora em USD

    Raises:
        ValueError: Se o tipo de instância ou região forem inválidos
    """
    try:
        return aws_resources.get_ec2_base_price(instance_type, region, operating_system)
    except Exception as e:
        logger.error(f"Erro ao obter preço estático para EC2: {e}")
        raise


def get_ebs_price_static(volume_type: str, region: str) -> float:
    """
    Obtém o preço estático de um volume EBS por GB-mês.

    Args:
        volume_type: Tipo de volume EBS (ex: 'gp2', 'io1')
        region: Região AWS (ex: 'us-east-1')

    Returns:
        float: Preço por GB-mês em USD

    Raises:
        ValueError: Se o tipo de volume ou região forem inválidos
    """
    try:
        return aws_resources.get_ebs_price(volume_type, region)
    except Exception as e:
        logger.error(f"Erro ao obter preço estático para EBS: {e}")
        raise
