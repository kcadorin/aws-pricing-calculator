"""
Módulo com dados estáticos de recursos da AWS.

Este módulo contém informações pré-definidas sobre tipos de instâncias EC2,
preços base, especificações de instâncias e outras informações úteis para
cálculos de preço quando o acesso à API da AWS não está disponível.
"""

from typing import Dict, Any, List, Optional, Union

# Lista de regiões suportadas pela AWS
AWS_REGIONS = [
    "us-east-1",  # Norte da Virgínia
    "us-east-2",  # Ohio
    "us-west-1",  # Norte da Califórnia
    "us-west-2",  # Oregon
    "af-south-1",  # Cidade do Cabo
    "ap-east-1",  # Hong Kong
    "ap-south-1",  # Mumbai
    "ap-northeast-1",  # Tóquio
    "ap-northeast-2",  # Seul
    "ap-northeast-3",  # Osaka
    "ap-southeast-1",  # Singapura
    "ap-southeast-2",  # Sydney
    "ca-central-1",  # Central do Canadá
    "eu-central-1",  # Frankfurt
    "eu-west-1",  # Irlanda
    "eu-west-2",  # Londres
    "eu-west-3",  # Paris
    "eu-south-1",  # Milão
    "eu-north-1",  # Estocolmo
    "me-south-1",  # Barém
    "sa-east-1",  # São Paulo
]

# Definições de famílias de instâncias EC2
INSTANCE_FAMILIES = {
    "t2": "Burstable Performance",
    "t3": "Burstable Performance",
    "t4g": "Burstable ARM-based Performance",
    "m5": "General Purpose",
    "m6g": "ARM-based General Purpose",
    "c5": "Compute Optimized",
    "c6g": "ARM-based Compute Optimized",
    "r5": "Memory Optimized",
    "r6g": "ARM-based Memory Optimized",
    "x1": "Memory Optimized",
    "z1d": "Memory Optimized with High Frequency",
    "p3": "GPU Optimized",
    "g4": "GPU Optimized",
    "i3": "Storage Optimized",
    "d2": "Storage Optimized",
}

# Exemplo de preços base para instâncias EC2 por hora em USD
# Valores aproximados por região, para caso de uso offline
EC2_BASE_PRICES = {
    # t2 family
    "t2.nano": {
        "us-east-1": 0.0058,
        "us-east-2": 0.0052,
        "us-west-1": 0.0069,
        "us-west-2": 0.0059,
        "eu-west-1": 0.0063,
        "ap-northeast-1": 0.0074,
        "default": 0.0065,  # Preço padrão para regiões não listadas
    },
    "t2.micro": {
        "us-east-1": 0.0116,
        "us-east-2": 0.0104,
        "us-west-1": 0.0139,
        "us-west-2": 0.0117,
        "eu-west-1": 0.0127,
        "ap-northeast-1": 0.0146,
        "default": 0.0130,
    },
    "t2.small": {
        "us-east-1": 0.023,
        "us-east-2": 0.0207,
        "us-west-1": 0.0275,
        "us-west-2": 0.0233,
        "eu-west-1": 0.0250,
        "ap-northeast-1": 0.0292,
        "default": 0.0260,
    },
    "t2.medium": {
        "us-east-1": 0.0464,
        "us-east-2": 0.0418,
        "us-west-1": 0.0555,
        "us-west-2": 0.0468,
        "eu-west-1": 0.0504,
        "ap-northeast-1": 0.0584,
        "default": 0.0520,
    },
    "t2.large": {
        "us-east-1": 0.0928,
        "us-east-2": 0.0835,
        "us-west-1": 0.1109,
        "us-west-2": 0.0936,
        "eu-west-1": 0.1008,
        "ap-northeast-1": 0.1168,
        "default": 0.1040,
    },
    "t2.xlarge": {
        "us-east-1": 0.1856,
        "us-east-2": 0.1670,
        "us-west-1": 0.2219,
        "us-west-2": 0.1872,
        "eu-west-1": 0.2016,
        "ap-northeast-1": 0.2336,
        "default": 0.2080,
    },
    "t2.2xlarge": {
        "us-east-1": 0.3712,
        "us-east-2": 0.3341,
        "us-west-1": 0.4438,
        "us-west-2": 0.3744,
        "eu-west-1": 0.4032,
        "ap-northeast-1": 0.4672,
        "default": 0.4160,
    },
    # t3 family
    "t3.nano": {
        "us-east-1": 0.0052,
        "us-east-2": 0.0047,
        "us-west-1": 0.0062,
        "us-west-2": 0.0052,
        "eu-west-1": 0.0057,
        "ap-northeast-1": 0.0066,
        "default": 0.0059,
    },
    "t3.micro": {
        "us-east-1": 0.0104,
        "us-east-2": 0.0094,
        "us-west-1": 0.0125,
        "us-west-2": 0.0104,
        "eu-west-1": 0.0114,
        "ap-northeast-1": 0.0132,
        "default": 0.0117,
    },
    "t3.small": {
        "us-east-1": 0.0208,
        "us-east-2": 0.0187,
        "us-west-1": 0.0250,
        "us-west-2": 0.0208,
        "eu-west-1": 0.0227,
        "ap-northeast-1": 0.0264,
        "default": 0.0234,
    },
    # m5 family
    "m5.large": {
        "us-east-1": 0.096,
        "us-east-2": 0.086,
        "us-west-1": 0.113,
        "us-west-2": 0.096,
        "eu-west-1": 0.105,
        "ap-northeast-1": 0.121,
        "default": 0.107,
    },
    "m5.xlarge": {
        "us-east-1": 0.192,
        "us-east-2": 0.173,
        "us-west-1": 0.226,
        "us-west-2": 0.192,
        "eu-west-1": 0.210,
        "ap-northeast-1": 0.242,
        "default": 0.215,
    },
    "m5.2xlarge": {
        "us-east-1": 0.384,
        "us-east-2": 0.346,
        "us-west-1": 0.452,
        "us-west-2": 0.384,
        "eu-west-1": 0.419,
        "ap-northeast-1": 0.484,
        "default": 0.430,
    },
    # c5 family
    "c5.large": {
        "us-east-1": 0.085,
        "us-east-2": 0.077,
        "us-west-1": 0.101,
        "us-west-2": 0.085,
        "eu-west-1": 0.093,
        "ap-northeast-1": 0.108,
        "default": 0.095,
    },
    "c5.xlarge": {
        "us-east-1": 0.170,
        "us-east-2": 0.154,
        "us-west-1": 0.202,
        "us-west-2": 0.170,
        "eu-west-1": 0.186,
        "ap-northeast-1": 0.216,
        "default": 0.190,
    },
    "c5.2xlarge": {
        "us-east-1": 0.340,
        "us-east-2": 0.308,
        "us-west-1": 0.404,
        "us-west-2": 0.340,
        "eu-west-1": 0.372,
        "ap-northeast-1": 0.432,
        "default": 0.380,
    },
    # r5 family
    "r5.large": {
        "us-east-1": 0.126,
        "us-east-2": 0.113,
        "us-west-1": 0.149,
        "us-west-2": 0.126,
        "eu-west-1": 0.139,
        "ap-northeast-1": 0.160,
        "default": 0.141,
    },
    "r5.xlarge": {
        "us-east-1": 0.252,
        "us-east-2": 0.226,
        "us-west-1": 0.298,
        "us-west-2": 0.252,
        "eu-west-1": 0.278,
        "ap-northeast-1": 0.320,
        "default": 0.282,
    },
    "r5.2xlarge": {
        "us-east-1": 0.504,
        "us-east-2": 0.452,
        "us-west-1": 0.596,
        "us-west-2": 0.504,
        "eu-west-1": 0.556,
        "ap-northeast-1": 0.640,
        "default": 0.564,
    },
}

# Preços Windows acrescentam um valor adicional ao preço Linux
WINDOWS_PRICE_PREMIUM = 0.058  # $0.058 por hora adicional para Windows

# Preços para volumes EBS por GB-mês
EBS_PRICES = {
    "gp2": {  # General Purpose SSD
        "us-east-1": 0.10,
        "us-east-2": 0.10,
        "us-west-1": 0.11,
        "us-west-2": 0.10,
        "eu-west-1": 0.11,
        "ap-northeast-1": 0.12,
        "default": 0.11,
    },
    "gp3": {  # General Purpose SSD v3
        "us-east-1": 0.08,
        "us-east-2": 0.08,
        "us-west-1": 0.09,
        "us-west-2": 0.08,
        "eu-west-1": 0.09,
        "ap-northeast-1": 0.09,
        "default": 0.09,
    },
    "io1": {  # Provisioned IOPS SSD
        "us-east-1": 0.125,
        "us-east-2": 0.125,
        "us-west-1": 0.138,
        "us-west-2": 0.125,
        "eu-west-1": 0.138,
        "ap-northeast-1": 0.142,
        "default": 0.135,
    },
    "st1": {  # Throughput Optimized HDD
        "us-east-1": 0.045,
        "us-east-2": 0.045,
        "us-west-1": 0.05,
        "us-west-2": 0.045,
        "eu-west-1": 0.05,
        "ap-northeast-1": 0.055,
        "default": 0.05,
    },
    "sc1": {  # Cold HDD
        "us-east-1": 0.025,
        "us-east-2": 0.025,
        "us-west-1": 0.027,
        "us-west-2": 0.025,
        "eu-west-1": 0.027,
        "ap-northeast-1": 0.03,
        "default": 0.027,
    },
    "standard": {  # Magnetic (legacy)
        "us-east-1": 0.05,
        "us-east-2": 0.05,
        "us-west-1": 0.055,
        "us-west-2": 0.05,
        "eu-west-1": 0.055,
        "ap-northeast-1": 0.06,
        "default": 0.055,
    },
}

# Especificações de tipos de instância EC2
INSTANCE_SPECS = {
    # t2 family
    "t2.nano": {
        "vcpus": 1,
        "memory_gb": 0.5,
        "storage_gb": 0,
        "network": "Low to Moderate",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t2.micro": {
        "vcpus": 1,
        "memory_gb": 1,
        "storage_gb": 0,
        "network": "Low to Moderate",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t2.small": {
        "vcpus": 1,
        "memory_gb": 2,
        "storage_gb": 0,
        "network": "Low to Moderate",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t2.medium": {
        "vcpus": 2,
        "memory_gb": 4,
        "storage_gb": 0,
        "network": "Low to Moderate",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t2.large": {
        "vcpus": 2,
        "memory_gb": 8,
        "storage_gb": 0,
        "network": "Low to Moderate",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t2.xlarge": {
        "vcpus": 4,
        "memory_gb": 16,
        "storage_gb": 0,
        "network": "Moderate",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t2.2xlarge": {
        "vcpus": 8,
        "memory_gb": 32,
        "storage_gb": 0,
        "network": "Moderate",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    # t3 family
    "t3.nano": {
        "vcpus": 2,
        "memory_gb": 0.5,
        "storage_gb": 0,
        "network": "Up to 5 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t3.micro": {
        "vcpus": 2,
        "memory_gb": 1,
        "storage_gb": 0,
        "network": "Up to 5 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t3.small": {
        "vcpus": 2,
        "memory_gb": 2,
        "storage_gb": 0,
        "network": "Up to 5 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t3.medium": {
        "vcpus": 2,
        "memory_gb": 4,
        "storage_gb": 0,
        "network": "Up to 5 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t3.large": {
        "vcpus": 2,
        "memory_gb": 8,
        "storage_gb": 0,
        "network": "Up to 5 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t3.xlarge": {
        "vcpus": 4,
        "memory_gb": 16,
        "storage_gb": 0,
        "network": "Up to 5 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "t3.2xlarge": {
        "vcpus": 8,
        "memory_gb": 32,
        "storage_gb": 0,
        "network": "Up to 5 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    # m5 family
    "m5.large": {
        "vcpus": 2,
        "memory_gb": 8,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "m5.xlarge": {
        "vcpus": 4,
        "memory_gb": 16,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "m5.2xlarge": {
        "vcpus": 8,
        "memory_gb": 32,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "m5.4xlarge": {
        "vcpus": 16,
        "memory_gb": 64,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    # c5 family
    "c5.large": {
        "vcpus": 2,
        "memory_gb": 4,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "c5.xlarge": {
        "vcpus": 4,
        "memory_gb": 8,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "c5.2xlarge": {
        "vcpus": 8,
        "memory_gb": 16,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "c5.4xlarge": {
        "vcpus": 16,
        "memory_gb": 32,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    # r5 family
    "r5.large": {
        "vcpus": 2,
        "memory_gb": 16,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "r5.xlarge": {
        "vcpus": 4,
        "memory_gb": 32,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "r5.2xlarge": {
        "vcpus": 8,
        "memory_gb": 64,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
    "r5.4xlarge": {
        "vcpus": 16,
        "memory_gb": 128,
        "storage_gb": 0,
        "network": "Up to 10 Gigabit",
        "architecture": ["x86_64"],
        "current_generation": True,
    },
}


# Funções para acessar os dados estáticos


def is_valid_region(region: str) -> bool:
    """
    Verifica se a região especificada é válida.

    Args:
        region: Região AWS para verificar.

    Returns:
        True se a região for válida, False caso contrário.
    """
    return region in AWS_REGIONS


def is_valid_instance_type(instance_type: str) -> bool:
    """
    Verifica se o tipo de instância especificado é válido.

    Args:
        instance_type: Tipo de instância EC2 para verificar.

    Returns:
        True se o tipo de instância for válido, False caso contrário.
    """
    return instance_type in INSTANCE_SPECS


def get_all_instance_types() -> List[str]:
    """
    Retorna todos os tipos de instância disponíveis nos dados estáticos.

    Returns:
        Lista de tipos de instância.
    """
    return list(INSTANCE_SPECS.keys())


def get_instance_type_specs(instance_type: str) -> Dict[str, Any]:
    """
    Retorna as especificações para o tipo de instância especificado.

    Args:
        instance_type: Tipo de instância EC2.

    Returns:
        Dicionário com especificações da instância ou None se não encontrado.
    """
    return INSTANCE_SPECS.get(instance_type)


def get_ec2_base_price(
    instance_type: str, region: str, operating_system: str = "Linux"
) -> float:
    """
    Retorna o preço base por hora para o tipo de instância e região especificados.

    Args:
        instance_type: Tipo de instância EC2.
        region: Região AWS.
        operating_system: Sistema operacional ("Linux" ou "Windows").

    Returns:
        Preço por hora em USD.

    Raises:
        ValueError: Se o tipo de instância ou região não forem válidos.
    """
    if not is_valid_instance_type(instance_type):
        raise ValueError(f"Tipo de instância inválido: {instance_type}")

    # Obter preço base para Linux
    instance_prices = EC2_BASE_PRICES.get(instance_type, {})
    base_price = instance_prices.get(region, instance_prices.get("default", 0))

    # Adicionar premium para Windows
    if operating_system.lower() == "windows":
        base_price += WINDOWS_PRICE_PREMIUM

    return base_price


def get_ebs_price(volume_type: str, region: str) -> float:
    """
    Retorna o preço por GB-mês para o tipo de volume EBS e região especificados.

    Args:
        volume_type: Tipo de volume EBS (ex: gp2, io1).
        region: Região AWS.

    Returns:
        Preço por GB-mês em USD.

    Raises:
        ValueError: Se o tipo de volume não for válido.
    """
    if volume_type not in EBS_PRICES:
        raise ValueError(f"Tipo de volume EBS inválido: {volume_type}")

    volume_prices = EBS_PRICES.get(volume_type, {})
    return volume_prices.get(region, volume_prices.get("default", 0))
