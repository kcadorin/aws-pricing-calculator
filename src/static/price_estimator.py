"""
Biblioteca para estimar preços de recursos AWS quando a API oficial não está disponível.
Fornece estimativas aproximadas baseadas em multiplicadores comuns para diferentes tipos
de instâncias, regiões e sistemas operacionais.
"""

import logging
import re
from typing import Dict, Tuple, Optional, Any

# Configure o logger
logger = logging.getLogger(__name__)

# Multiplicadores de preço por família de instância
# Valores relativos a uma instância t2 (base 1.0)
FAMILY_MULTIPLIERS = {
    "t2": 1.0,
    "t3": 0.9,  # T3 é geralmente ~10% mais barato que T2
    "t3a": 0.8,  # T3a é geralmente ~20% mais barato que T2
    "t4g": 0.7,  # T4g é geralmente ~30% mais barato que T2 (ARM)
    "m5": 2.2,  # Uso geral, maior que T2
    "m5a": 2.0,  # Uso geral AMD, um pouco mais barato
    "m5n": 2.4,  # Uso geral com mais rede
    "m6g": 2.0,  # Uso geral ARM
    "m6i": 2.2,  # Uso geral Intel mais recente
    "c5": 2.0,  # Otimizado para computação
    "c5a": 1.8,  # Otimizado para computação AMD
    "c5n": 2.2,  # Otimizado para computação com mais rede
    "c6g": 1.8,  # Otimizado para computação ARM
    "c6i": 2.0,  # Otimizado para computação Intel mais recente
    "r5": 2.8,  # Otimizado para memória
    "r5a": 2.6,  # Otimizado para memória AMD
    "r5n": 3.0,  # Otimizado para memória com mais rede
    "r6g": 2.5,  # Otimizado para memória ARM
    "r6i": 2.8,  # Otimizado para memória Intel mais recente
    "x1": 12.0,  # Memória extrema
    "x1e": 16.0,  # Memória extrema otimizada
    "x2gd": 14.0,  # Memória extrema ARM
    "d2": 3.5,  # Otimizado para armazenamento HDD
    "d3": 3.2,  # Otimizado para armazenamento HDD mais recente
    "h1": 3.8,  # Otimizado para armazenamento HDD de alta densidade
    "i3": 4.0,  # Otimizado para armazenamento SSD
    "i3en": 4.5,  # Otimizado para armazenamento SSD com mais rede
    "p3": 15.0,  # GPU
    "p4d": 30.0,  # GPU de alto desempenho
    "g4dn": 12.0,  # GPU de uso geral
    "g5": 18.0,  # GPU de última geração
}

# Multiplicadores de preço por tamanho de instância
# Com base no número de vCPUs, com algumas variações específicas de família
SIZE_MULTIPLIERS = {
    "nano": 0.25,
    "micro": 0.5,
    "small": 1.0,
    "medium": 2.0,
    "large": 4.0,
    "xlarge": 8.0,
    "2xlarge": 16.0,
    "3xlarge": 24.0,
    "4xlarge": 32.0,
    "6xlarge": 48.0,
    "8xlarge": 64.0,
    "9xlarge": 72.0,
    "10xlarge": 80.0,
    "12xlarge": 96.0,
    "16xlarge": 128.0,
    "18xlarge": 144.0,
    "24xlarge": 192.0,
    "32xlarge": 256.0,
    "48xlarge": 384.0,
    "metal": 128.0,  # Varia por família, mas esta é uma aproximação
}

# Multiplicadores de preço por região
# us-east-1 (Norte da Virgínia) como referência (1.0)
REGION_MULTIPLIERS = {
    "us-east-1": 1.0,  # Norte da Virgínia (referência)
    "us-east-2": 1.0,  # Ohio
    "us-west-1": 1.08,  # Califórnia do Norte (~8% mais caro)
    "us-west-2": 1.02,  # Oregon (~2% mais caro)
    "ca-central-1": 1.07,  # Canadá
    "eu-north-1": 1.05,  # Estocolmo
    "eu-west-1": 1.02,  # Irlanda
    "eu-west-2": 1.10,  # Londres
    "eu-west-3": 1.10,  # Paris
    "eu-central-1": 1.15,  # Frankfurt
    "eu-south-1": 1.12,  # Milão
    "ap-northeast-1": 1.20,  # Tóquio
    "ap-northeast-2": 1.20,  # Seul
    "ap-northeast-3": 1.20,  # Osaka
    "ap-southeast-1": 1.18,  # Singapura
    "ap-southeast-2": 1.22,  # Sydney
    "ap-east-1": 1.25,  # Hong Kong
    "ap-south-1": 1.15,  # Mumbai
    "sa-east-1": 1.30,  # São Paulo
    "me-south-1": 1.25,  # Bahrein
    "af-south-1": 1.25,  # Cidade do Cabo
}

# Multiplicadores de preço por sistema operacional
# Linux como referência (1.0)
OS_MULTIPLIERS = {
    "Linux": 1.0,
    "RHEL": 1.3,  # Red Hat Enterprise Linux (mais caro devido à licença)
    "SUSE": 1.25,  # SUSE Linux (mais caro devido à licença)
    "Windows": 2.0,  # Windows (aproximadamente 2x o custo do Linux)
    "Linux with SQL Web": 1.8,  # Linux com SQL Web
    "Linux with SQL Std": 4.5,  # Linux com SQL Standard
    "Linux with SQL Ent": 12.0,  # Linux com SQL Enterprise
    "Windows with SQL Web": 2.8,  # Windows com SQL Web
    "Windows with SQL Std": 5.5,  # Windows com SQL Standard
    "Windows with SQL Ent": 14.0,  # Windows com SQL Enterprise
}


def parse_instance_type(instance_type: str) -> Tuple[str, str]:
    """
    Extrai a família e o tamanho de um tipo de instância EC2.

    Args:
        instance_type: String representando o tipo de instância (ex: "t2.micro")

    Returns:
        Tupla contendo (família, tamanho)

    Raises:
        ValueError: Se o formato do tipo de instância for inválido
    """
    # Regex para extrair família e tamanho do tipo de instância
    pattern = r"([a-z]+[0-9][a-z]*)\.([a-z0-9]+)"
    match = re.match(pattern, instance_type)

    if not match:
        raise ValueError(f"Formato de tipo de instância inválido: {instance_type}")

    family = match.group(1)
    size = match.group(2)

    return family, size


def estimate_ec2_price(
    instance_type: str,
    region: str = "us-east-1",
    os: str = "Linux",
    base_price: Optional[float] = None,
) -> float:
    """
    Estima o preço de uma instância EC2 baseado no tipo, região e sistema operacional.

    Args:
        instance_type: Tipo da instância EC2 (ex: "t2.micro")
        region: Código da região AWS (padrão: "us-east-1")
        os: Sistema operacional (padrão: "Linux")
        base_price: Preço base opcional para cálculo (se não for fornecido,
                    um preço de referência será usado)

    Returns:
        Preço estimado por hora em USD

    Raises:
        ValueError: Se os parâmetros forem inválidos
    """
    # Extrai a família e o tamanho da instância
    family, size = parse_instance_type(instance_type)

    # Verifica se os multiplicadores existem
    if family not in FAMILY_MULTIPLIERS:
        logger.warning(
            f"Família de instância desconhecida: {family}. Usando multiplicador padrão 1.0"
        )
        family_multiplier = 1.0
    else:
        family_multiplier = FAMILY_MULTIPLIERS[family]

    if size not in SIZE_MULTIPLIERS:
        logger.warning(
            f"Tamanho de instância desconhecido: {size}. Usando multiplicador padrão 1.0"
        )
        size_multiplier = 1.0
    else:
        size_multiplier = SIZE_MULTIPLIERS[size]

    if region not in REGION_MULTIPLIERS:
        logger.warning(
            f"Região desconhecida: {region}. Usando multiplicador padrão 1.0"
        )
        region_multiplier = 1.0
    else:
        region_multiplier = REGION_MULTIPLIERS[region]

    if os not in OS_MULTIPLIERS:
        logger.warning(
            f"Sistema operacional desconhecido: {os}. Usando multiplicador do Linux (1.0)"
        )
        os_multiplier = 1.0
    else:
        os_multiplier = OS_MULTIPLIERS[os]

    # Se o preço base não for fornecido, use um valor de referência
    if base_price is None:
        from .aws_resources import BASE_PRICES

        if instance_type in BASE_PRICES:
            # Usamos o preço base diretamente se disponível
            base_price = BASE_PRICES[instance_type]

            # Como já temos o preço base desta instância específica,
            # ajustamos apenas pela região e SO
            estimated_price = base_price * region_multiplier * os_multiplier

            logger.info(
                f"Usando preço base conhecido para {instance_type}: ${base_price:.4f}/hora. "
                f"Preço estimado com ajustes de região ({region}) e SO ({os}): ${estimated_price:.4f}/hora"
            )
            return estimated_price
        else:
            # Referência: t2.micro Linux em us-east-1 = $0.0116/hora
            base_price = 0.0116
            logger.info(
                f"Sem preço base para {instance_type}. Usando t2.micro como referência: ${base_price:.4f}/hora"
            )

    # Calcula o preço estimado usando multiplicadores
    estimated_price = (
        base_price
        * family_multiplier
        * size_multiplier
        * region_multiplier
        * os_multiplier
    )

    logger.info(
        f"Estimativa para {instance_type} ({os}) em {region}: ${estimated_price:.4f}/hora. "
        f"Multiplicadores: família={family_multiplier:.2f}, tamanho={size_multiplier:.2f}, "
        f"região={region_multiplier:.2f}, SO={os_multiplier:.2f}"
    )

    return estimated_price
