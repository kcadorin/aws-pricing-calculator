"""
Serviço para obtenção de informações de preços da AWS.

Este módulo fornece funções para consultar os preços de instâncias EC2
e outros recursos da AWS, com suporte para modo online (via API AWS)
e offline (via dados estáticos).
"""

import os
import json
import logging
import boto3
from typing import Dict, Any, Optional, List, Union

from utils.offline_mode import is_aws_online, with_fallback
from static.aws_resources import (
    get_instance_type_specs,
    get_ec2_base_price,
    get_ebs_price,
    is_valid_instance_type,
    is_valid_region,
    get_all_instance_types,
)

# Configuração do logger
logger = logging.getLogger(__name__)

# Cliente do serviço de preços da AWS
_pricing_client = None


def get_pricing_client():
    """
    Retorna um cliente para o serviço de preços da AWS.
    Reutiliza a conexão se já estiver estabelecida.

    Returns:
        Cliente do serviço AWS Pricing
    """
    global _pricing_client

    if _pricing_client is None and is_aws_online():
        try:
            _pricing_client = boto3.client("pricing", region_name="us-east-1")
            logger.debug("Cliente do serviço de preços AWS inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente de preços AWS: {str(e)}")
            return None

    return _pricing_client


@with_fallback
def get_ec2_price(
    instance_type: str, region: str, operating_system: str = "Linux"
) -> Dict[str, Any]:
    """
    Obtém o preço atual de uma instância EC2 a partir da API da AWS.

    Args:
        instance_type: Tipo de instância EC2 (ex: t2.micro)
        region: Região da AWS (ex: us-east-1)
        operating_system: Sistema operacional (ex: Linux, Windows)

    Returns:
        Dicionário com informações de preço
    """
    client = get_pricing_client()
    if not client:
        raise ConnectionError("Não foi possível conectar à API de preços da AWS")

    # Filtros para o tipo de instância e região
    filters = [
        {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
        {"Type": "TERM_MATCH", "Field": "location", "Value": region},
        {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": operating_system},
        {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
        {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
        {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
    ]

    response = client.get_products(ServiceCode="AmazonEC2", Filters=filters)

    # Processa os resultados
    for product_str in response.get("PriceList", []):
        product = json.loads(product_str)
        terms = product.get("terms", {})
        on_demand = next(iter(terms.get("OnDemand", {}).values()))
        price_dimensions = next(iter(on_demand.get("priceDimensions", {}).values()))

        # Extrai a unidade de preço e o valor
        unit = price_dimensions.get("unit", "")
        price_per_unit = price_dimensions.get("pricePerUnit", {})
        price = float(price_per_unit.get("USD", 0))

        # Retorna os detalhes da instância com o preço
        return {
            "instance_type": instance_type,
            "region": region,
            "operating_system": operating_system,
            "price_per_hour": price,
            "unit": unit,
            "currency": "USD",
        }

    # Se não encontrou o preço, registra um aviso e lança exceção
    logger.warning(
        f"Preço não encontrado para instância {instance_type} na região {region}"
    )
    raise ValueError(
        f"Preço não encontrado para instância {instance_type} na região {region}"
    )


def get_ec2_price_static(
    instance_type: str, region: str, operating_system: str = "Linux"
) -> Dict[str, Any]:
    """
    Versão offline para obter o preço de uma instância EC2 usando dados estáticos.

    Args:
        instance_type: Tipo de instância EC2 (ex: t2.micro)
        region: Região da AWS (ex: us-east-1)
        operating_system: Sistema operacional (ex: Linux, Windows)

    Returns:
        Dicionário com informações de preço
    """
    if not is_valid_instance_type(instance_type):
        raise ValueError(f"Tipo de instância inválido: {instance_type}")

    if not is_valid_region(region):
        raise ValueError(f"Região inválida: {region}")

    # Obter preço do dicionário estático
    price = get_ec2_base_price(instance_type, region, operating_system)

    # Retorna os detalhes da instância com o preço
    return {
        "instance_type": instance_type,
        "region": region,
        "operating_system": operating_system,
        "price_per_hour": price,
        "unit": "Hrs",
        "currency": "USD",
        "source": "static_data",
    }


@with_fallback
def get_ebs_volume_price(volume_type: str, region: str, size_gb: int) -> Dict[str, Any]:
    """
    Obtém o preço atual de um volume EBS a partir da API da AWS.

    Args:
        volume_type: Tipo de volume EBS (ex: gp2, io1)
        region: Região da AWS (ex: us-east-1)
        size_gb: Tamanho do volume em GB

    Returns:
        Dicionário com informações de preço
    """
    client = get_pricing_client()
    if not client:
        raise ConnectionError("Não foi possível conectar à API de preços da AWS")

    # Mapeia o tipo de volume para o valor esperado pela API
    volume_api_name = {
        "gp2": "General Purpose",
        "gp3": "General Purpose",
        "io1": "Provisioned IOPS",
        "io2": "Provisioned IOPS",
        "st1": "Throughput Optimized HDD",
        "sc1": "Cold HDD",
        "standard": "Magnetic",
    }.get(volume_type.lower(), volume_type)

    # Filtros para o tipo de volume e região
    filters = [
        {"Type": "TERM_MATCH", "Field": "volumeType", "Value": volume_api_name},
        {"Type": "TERM_MATCH", "Field": "location", "Value": region},
    ]

    response = client.get_products(ServiceCode="AmazonEC2", Filters=filters)

    # Processa os resultados
    for product_str in response.get("PriceList", []):
        product = json.loads(product_str)
        terms = product.get("terms", {})
        on_demand = next(iter(terms.get("OnDemand", {}).values()))
        price_dimensions = next(iter(on_demand.get("priceDimensions", {}).values()))

        # Extrai a unidade de preço e o valor
        unit = price_dimensions.get("unit", "")
        price_per_unit = price_dimensions.get("pricePerUnit", {})
        price_per_gb = float(price_per_unit.get("USD", 0))
        total_price = price_per_gb * size_gb

        # Retorna os detalhes do volume com o preço
        return {
            "volume_type": volume_type,
            "region": region,
            "size_gb": size_gb,
            "price_per_gb_month": price_per_gb,
            "total_price_month": total_price,
            "unit": unit,
            "currency": "USD",
        }

    # Se não encontrou o preço, registra um aviso e lança exceção
    logger.warning(f"Preço não encontrado para volume {volume_type} na região {region}")
    raise ValueError(
        f"Preço não encontrado para volume {volume_type} na região {region}"
    )


def get_ebs_volume_price_static(
    volume_type: str, region: str, size_gb: int
) -> Dict[str, Any]:
    """
    Versão offline para obter o preço de um volume EBS usando dados estáticos.

    Args:
        volume_type: Tipo de volume EBS (ex: gp2, io1)
        region: Região da AWS (ex: us-east-1)
        size_gb: Tamanho do volume em GB

    Returns:
        Dicionário com informações de preço
    """
    if not is_valid_region(region):
        raise ValueError(f"Região inválida: {region}")

    # Obter preço por GB do dicionário estático
    price_per_gb = get_ebs_price(volume_type, region)
    total_price = price_per_gb * size_gb

    # Retorna os detalhes do volume com o preço
    return {
        "volume_type": volume_type,
        "region": region,
        "size_gb": size_gb,
        "price_per_gb_month": price_per_gb,
        "total_price_month": total_price,
        "unit": "GB-Mo",
        "currency": "USD",
        "source": "static_data",
    }


@with_fallback
def get_available_instance_types(region: str = None) -> List[str]:
    """
    Obtém a lista de tipos de instância disponíveis na AWS para uma região.

    Args:
        region: Região da AWS (opcional)

    Returns:
        Lista de tipos de instância disponíveis
    """
    client = boto3.client("ec2", region_name=region if region else "us-east-1")

    response = client.describe_instance_types()
    instance_types = [it["InstanceType"] for it in response.get("InstanceTypes", [])]

    # A API retorna os resultados paginados, então precisamos continuar
    # enquanto houver um token de próxima página
    while "NextToken" in response:
        response = client.describe_instance_types(NextToken=response["NextToken"])
        instance_types.extend(
            [it["InstanceType"] for it in response.get("InstanceTypes", [])]
        )

    return sorted(instance_types)


def get_available_instance_types_static(region: str = None) -> List[str]:
    """
    Versão offline para obter os tipos de instância disponíveis usando dados estáticos.

    Args:
        region: Região da AWS (opcional, não usado na versão estática)

    Returns:
        Lista de tipos de instância disponíveis
    """
    return sorted(get_all_instance_types())


@with_fallback
def get_instance_specs(instance_type: str) -> Dict[str, Any]:
    """
    Obtém as especificações de uma instância EC2 a partir da API da AWS.

    Args:
        instance_type: Tipo de instância EC2 (ex: t2.micro)

    Returns:
        Dicionário com as especificações da instância
    """
    client = boto3.client("ec2", region_name="us-east-1")

    response = client.describe_instance_types(InstanceTypes=[instance_type])

    if "InstanceTypes" in response and response["InstanceTypes"]:
        instance_info = response["InstanceTypes"][0]

        return {
            "instance_type": instance_type,
            "vcpu": instance_info.get("VCpuInfo", {}).get("DefaultVCpus", 0),
            "memory_gb": instance_info.get("MemoryInfo", {}).get("SizeInMiB", 0) / 1024,
            "storage": instance_info.get("InstanceStorageInfo", {}).get(
                "TotalSizeInGB", 0
            ),
            "network_performance": instance_info.get("NetworkInfo", {}).get(
                "NetworkPerformance", ""
            ),
            "architecture": instance_info.get("ProcessorInfo", {}).get(
                "SupportedArchitectures", []
            ),
            "is_current_generation": instance_info.get("CurrentGeneration", False),
        }

    # Se não encontrou as especificações, registra um aviso e lança exceção
    logger.warning(f"Especificações não encontradas para instância {instance_type}")
    raise ValueError(f"Especificações não encontradas para instância {instance_type}")


def get_instance_specs_static(instance_type: str) -> Dict[str, Any]:
    """
    Versão offline para obter as especificações de uma instância EC2 usando dados estáticos.

    Args:
        instance_type: Tipo de instância EC2 (ex: t2.micro)

    Returns:
        Dicionário com as especificações da instância
    """
    if not is_valid_instance_type(instance_type):
        raise ValueError(f"Tipo de instância inválido: {instance_type}")

    # Obter especificações do dicionário estático
    specs = get_instance_type_specs(instance_type)

    if not specs:
        raise ValueError(
            f"Especificações não encontradas para instância {instance_type}"
        )

    return {
        "instance_type": instance_type,
        "vcpu": specs.get("vcpus", 0),
        "memory_gb": specs.get("memory_gb", 0),
        "storage": specs.get("storage_gb", 0),
        "network_performance": specs.get("network", ""),
        "architecture": specs.get("architecture", ["x86_64"]),
        "is_current_generation": specs.get("current_generation", True),
        "source": "static_data",
    }
