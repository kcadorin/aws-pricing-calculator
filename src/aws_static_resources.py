import json
import os
from decimal import Decimal

# Dicionário com as famílias de instâncias EC2 mais recentes
EC2_INSTANCES = {
    # Família t - Propósito geral com capacidade de burst
    "t4g": [
        {"type": "t4g.nano", "vcpu": 2, "memory": "0.5 GiB", "arch": "arm64"},
        {"type": "t4g.micro", "vcpu": 2, "memory": "1 GiB", "arch": "arm64"},
        {"type": "t4g.small", "vcpu": 2, "memory": "2 GiB", "arch": "arm64"},
        {"type": "t4g.medium", "vcpu": 2, "memory": "4 GiB", "arch": "arm64"},
        {"type": "t4g.large", "vcpu": 2, "memory": "8 GiB", "arch": "arm64"},
        {"type": "t4g.xlarge", "vcpu": 4, "memory": "16 GiB", "arch": "arm64"},
        {"type": "t4g.2xlarge", "vcpu": 8, "memory": "32 GiB", "arch": "arm64"},
    ],
    "t3": [
        {"type": "t3.nano", "vcpu": 2, "memory": "0.5 GiB", "arch": "x86_64"},
        {"type": "t3.micro", "vcpu": 2, "memory": "1 GiB", "arch": "x86_64"},
        {"type": "t3.small", "vcpu": 2, "memory": "2 GiB", "arch": "x86_64"},
        {"type": "t3.medium", "vcpu": 2, "memory": "4 GiB", "arch": "x86_64"},
        {"type": "t3.large", "vcpu": 2, "memory": "8 GiB", "arch": "x86_64"},
        {"type": "t3.xlarge", "vcpu": 4, "memory": "16 GiB", "arch": "x86_64"},
        {"type": "t3.2xlarge", "vcpu": 8, "memory": "32 GiB", "arch": "x86_64"},
    ],
    # Família m - Propósito geral
    "m7g": [
        {"type": "m7g.medium", "vcpu": 1, "memory": "4 GiB", "arch": "arm64"},
        {"type": "m7g.large", "vcpu": 2, "memory": "8 GiB", "arch": "arm64"},
        {"type": "m7g.xlarge", "vcpu": 4, "memory": "16 GiB", "arch": "arm64"},
        {"type": "m7g.2xlarge", "vcpu": 8, "memory": "32 GiB", "arch": "arm64"},
        {"type": "m7g.4xlarge", "vcpu": 16, "memory": "64 GiB", "arch": "arm64"},
        {"type": "m7g.8xlarge", "vcpu": 32, "memory": "128 GiB", "arch": "arm64"},
        {"type": "m7g.12xlarge", "vcpu": 48, "memory": "192 GiB", "arch": "arm64"},
        {"type": "m7g.16xlarge", "vcpu": 64, "memory": "256 GiB", "arch": "arm64"},
        {"type": "m7g.metal", "vcpu": 64, "memory": "256 GiB", "arch": "arm64"},
    ],
    "m7i": [
        {"type": "m7i.large", "vcpu": 2, "memory": "8 GiB", "arch": "x86_64"},
        {"type": "m7i.xlarge", "vcpu": 4, "memory": "16 GiB", "arch": "x86_64"},
        {"type": "m7i.2xlarge", "vcpu": 8, "memory": "32 GiB", "arch": "x86_64"},
        {"type": "m7i.4xlarge", "vcpu": 16, "memory": "64 GiB", "arch": "x86_64"},
        {"type": "m7i.8xlarge", "vcpu": 32, "memory": "128 GiB", "arch": "x86_64"},
        {"type": "m7i.12xlarge", "vcpu": 48, "memory": "192 GiB", "arch": "x86_64"},
        {"type": "m7i.16xlarge", "vcpu": 64, "memory": "256 GiB", "arch": "x86_64"},
        {"type": "m7i.24xlarge", "vcpu": 96, "memory": "384 GiB", "arch": "x86_64"},
        {"type": "m7i.48xlarge", "vcpu": 192, "memory": "768 GiB", "arch": "x86_64"},
        {"type": "m7i.metal-24xl", "vcpu": 96, "memory": "384 GiB", "arch": "x86_64"},
        {"type": "m7i.metal-48xl", "vcpu": 192, "memory": "768 GiB", "arch": "x86_64"},
    ],
    "m6g": [
        {"type": "m6g.medium", "vcpu": 1, "memory": "4 GiB", "arch": "arm64"},
        {"type": "m6g.large", "vcpu": 2, "memory": "8 GiB", "arch": "arm64"},
        {"type": "m6g.xlarge", "vcpu": 4, "memory": "16 GiB", "arch": "arm64"},
        {"type": "m6g.2xlarge", "vcpu": 8, "memory": "32 GiB", "arch": "arm64"},
        {"type": "m6g.4xlarge", "vcpu": 16, "memory": "64 GiB", "arch": "arm64"},
        {"type": "m6g.8xlarge", "vcpu": 32, "memory": "128 GiB", "arch": "arm64"},
        {"type": "m6g.12xlarge", "vcpu": 48, "memory": "192 GiB", "arch": "arm64"},
        {"type": "m6g.16xlarge", "vcpu": 64, "memory": "256 GiB", "arch": "arm64"},
        {"type": "m6g.metal", "vcpu": 64, "memory": "256 GiB", "arch": "arm64"},
    ],
    "m6i": [
        {"type": "m6i.large", "vcpu": 2, "memory": "8 GiB", "arch": "x86_64"},
        {"type": "m6i.xlarge", "vcpu": 4, "memory": "16 GiB", "arch": "x86_64"},
        {"type": "m6i.2xlarge", "vcpu": 8, "memory": "32 GiB", "arch": "x86_64"},
        {"type": "m6i.4xlarge", "vcpu": 16, "memory": "64 GiB", "arch": "x86_64"},
        {"type": "m6i.8xlarge", "vcpu": 32, "memory": "128 GiB", "arch": "x86_64"},
        {"type": "m6i.12xlarge", "vcpu": 48, "memory": "192 GiB", "arch": "x86_64"},
        {"type": "m6i.16xlarge", "vcpu": 64, "memory": "256 GiB", "arch": "x86_64"},
        {"type": "m6i.24xlarge", "vcpu": 96, "memory": "384 GiB", "arch": "x86_64"},
        {"type": "m6i.32xlarge", "vcpu": 128, "memory": "512 GiB", "arch": "x86_64"},
    ],
    "m5": [
        {"type": "m5.large", "vcpu": 2, "memory": "8 GiB", "arch": "x86_64"},
        {"type": "m5.xlarge", "vcpu": 4, "memory": "16 GiB", "arch": "x86_64"},
        {"type": "m5.2xlarge", "vcpu": 8, "memory": "32 GiB", "arch": "x86_64"},
        {"type": "m5.4xlarge", "vcpu": 16, "memory": "64 GiB", "arch": "x86_64"},
        {"type": "m5.8xlarge", "vcpu": 32, "memory": "128 GiB", "arch": "x86_64"},
        {"type": "m5.12xlarge", "vcpu": 48, "memory": "192 GiB", "arch": "x86_64"},
        {"type": "m5.16xlarge", "vcpu": 64, "memory": "256 GiB", "arch": "x86_64"},
        {"type": "m5.24xlarge", "vcpu": 96, "memory": "384 GiB", "arch": "x86_64"},
    ],
    # Família c - Computação otimizada
    "c7g": [
        {"type": "c7g.medium", "vcpu": 1, "memory": "2 GiB", "arch": "arm64"},
        {"type": "c7g.large", "vcpu": 2, "memory": "4 GiB", "arch": "arm64"},
        {"type": "c7g.xlarge", "vcpu": 4, "memory": "8 GiB", "arch": "arm64"},
        {"type": "c7g.2xlarge", "vcpu": 8, "memory": "16 GiB", "arch": "arm64"},
        {"type": "c7g.4xlarge", "vcpu": 16, "memory": "32 GiB", "arch": "arm64"},
        {"type": "c7g.8xlarge", "vcpu": 32, "memory": "64 GiB", "arch": "arm64"},
        {"type": "c7g.12xlarge", "vcpu": 48, "memory": "96 GiB", "arch": "arm64"},
        {"type": "c7g.16xlarge", "vcpu": 64, "memory": "128 GiB", "arch": "arm64"},
    ],
    "c6g": [
        {"type": "c6g.medium", "vcpu": 1, "memory": "2 GiB", "arch": "arm64"},
        {"type": "c6g.large", "vcpu": 2, "memory": "4 GiB", "arch": "arm64"},
        {"type": "c6g.xlarge", "vcpu": 4, "memory": "8 GiB", "arch": "arm64"},
        {"type": "c6g.2xlarge", "vcpu": 8, "memory": "16 GiB", "arch": "arm64"},
        {"type": "c6g.4xlarge", "vcpu": 16, "memory": "32 GiB", "arch": "arm64"},
        {"type": "c6g.8xlarge", "vcpu": 32, "memory": "64 GiB", "arch": "arm64"},
        {"type": "c6g.12xlarge", "vcpu": 48, "memory": "96 GiB", "arch": "arm64"},
        {"type": "c6g.16xlarge", "vcpu": 64, "memory": "128 GiB", "arch": "arm64"},
    ],
    "c6i": [
        {"type": "c6i.large", "vcpu": 2, "memory": "4 GiB", "arch": "x86_64"},
        {"type": "c6i.xlarge", "vcpu": 4, "memory": "8 GiB", "arch": "x86_64"},
        {"type": "c6i.2xlarge", "vcpu": 8, "memory": "16 GiB", "arch": "x86_64"},
        {"type": "c6i.4xlarge", "vcpu": 16, "memory": "32 GiB", "arch": "x86_64"},
        {"type": "c6i.8xlarge", "vcpu": 32, "memory": "64 GiB", "arch": "x86_64"},
        {"type": "c6i.12xlarge", "vcpu": 48, "memory": "96 GiB", "arch": "x86_64"},
        {"type": "c6i.16xlarge", "vcpu": 64, "memory": "128 GiB", "arch": "x86_64"},
        {"type": "c6i.24xlarge", "vcpu": 96, "memory": "192 GiB", "arch": "x86_64"},
        {"type": "c6i.32xlarge", "vcpu": 128, "memory": "256 GiB", "arch": "x86_64"},
    ],
    # Família r - Otimizada para memória
    "r7g": [
        {"type": "r7g.medium", "vcpu": 1, "memory": "8 GiB", "arch": "arm64"},
        {"type": "r7g.large", "vcpu": 2, "memory": "16 GiB", "arch": "arm64"},
        {"type": "r7g.xlarge", "vcpu": 4, "memory": "32 GiB", "arch": "arm64"},
        {"type": "r7g.2xlarge", "vcpu": 8, "memory": "64 GiB", "arch": "arm64"},
        {"type": "r7g.4xlarge", "vcpu": 16, "memory": "128 GiB", "arch": "arm64"},
        {"type": "r7g.8xlarge", "vcpu": 32, "memory": "256 GiB", "arch": "arm64"},
        {"type": "r7g.12xlarge", "vcpu": 48, "memory": "384 GiB", "arch": "arm64"},
        {"type": "r7g.16xlarge", "vcpu": 64, "memory": "512 GiB", "arch": "arm64"},
    ],
    "r6g": [
        {"type": "r6g.medium", "vcpu": 1, "memory": "8 GiB", "arch": "arm64"},
        {"type": "r6g.large", "vcpu": 2, "memory": "16 GiB", "arch": "arm64"},
        {"type": "r6g.xlarge", "vcpu": 4, "memory": "32 GiB", "arch": "arm64"},
        {"type": "r6g.2xlarge", "vcpu": 8, "memory": "64 GiB", "arch": "arm64"},
        {"type": "r6g.4xlarge", "vcpu": 16, "memory": "128 GiB", "arch": "arm64"},
        {"type": "r6g.8xlarge", "vcpu": 32, "memory": "256 GiB", "arch": "arm64"},
        {"type": "r6g.12xlarge", "vcpu": 48, "memory": "384 GiB", "arch": "arm64"},
        {"type": "r6g.16xlarge", "vcpu": 64, "memory": "512 GiB", "arch": "arm64"},
    ],
    "r6i": [
        {"type": "r6i.large", "vcpu": 2, "memory": "16 GiB", "arch": "x86_64"},
        {"type": "r6i.xlarge", "vcpu": 4, "memory": "32 GiB", "arch": "x86_64"},
        {"type": "r6i.2xlarge", "vcpu": 8, "memory": "64 GiB", "arch": "x86_64"},
        {"type": "r6i.4xlarge", "vcpu": 16, "memory": "128 GiB", "arch": "x86_64"},
        {"type": "r6i.8xlarge", "vcpu": 32, "memory": "256 GiB", "arch": "x86_64"},
        {"type": "r6i.12xlarge", "vcpu": 48, "memory": "384 GiB", "arch": "x86_64"},
        {"type": "r6i.16xlarge", "vcpu": 64, "memory": "512 GiB", "arch": "x86_64"},
        {"type": "r6i.24xlarge", "vcpu": 96, "memory": "768 GiB", "arch": "x86_64"},
        {"type": "r6i.32xlarge", "vcpu": 128, "memory": "1024 GiB", "arch": "x86_64"},
    ],
    # Família g - Otimizadas para GPU
    "g5": [
        {
            "type": "g5.xlarge",
            "vcpu": 4,
            "memory": "16 GiB",
            "arch": "x86_64",
            "gpu": "1x NVIDIA A10G",
        },
        {
            "type": "g5.2xlarge",
            "vcpu": 8,
            "memory": "32 GiB",
            "arch": "x86_64",
            "gpu": "1x NVIDIA A10G",
        },
        {
            "type": "g5.4xlarge",
            "vcpu": 16,
            "memory": "64 GiB",
            "arch": "x86_64",
            "gpu": "1x NVIDIA A10G",
        },
        {
            "type": "g5.8xlarge",
            "vcpu": 32,
            "memory": "128 GiB",
            "arch": "x86_64",
            "gpu": "1x NVIDIA A10G",
        },
        {
            "type": "g5.12xlarge",
            "vcpu": 48,
            "memory": "192 GiB",
            "arch": "x86_64",
            "gpu": "4x NVIDIA A10G",
        },
        {
            "type": "g5.16xlarge",
            "vcpu": 64,
            "memory": "256 GiB",
            "arch": "x86_64",
            "gpu": "1x NVIDIA A10G",
        },
        {
            "type": "g5.24xlarge",
            "vcpu": 96,
            "memory": "384 GiB",
            "arch": "x86_64",
            "gpu": "4x NVIDIA A10G",
        },
        {
            "type": "g5.48xlarge",
            "vcpu": 192,
            "memory": "768 GiB",
            "arch": "x86_64",
            "gpu": "8x NVIDIA A10G",
        },
    ],
}

# Classes de armazenamento S3
S3_STORAGE_CLASSES = [
    "Standard",
    "Intelligent-Tiering",
    "Standard-IA",
    "One Zone-IA",
    "Glacier Instant Retrieval",
    "Glacier Flexible Retrieval",
    "Glacier Deep Archive",
    "Outposts",
    "S3 Express One Zone",
]

# Recursos ECS/Fargate
FARGATE_RESOURCES = {
    "memory": [
        "0.5 GB",
        "1 GB",
        "2 GB",
        "3 GB",
        "4 GB",
        "5 GB",
        "6 GB",
        "7 GB",
        "8 GB",
        "16 GB",
        "30 GB",
    ],
    "vcpu": [
        "0.25 vCPU",
        "0.5 vCPU",
        "1 vCPU",
        "2 vCPU",
        "4 vCPU",
        "8 vCPU",
        "16 vCPU",
    ],
    "operating-system": ["Linux", "Windows"],
}

# Recursos Lambda
LAMBDA_RESOURCES = {
    "memory": [
        "128 MB",
        "256 MB",
        "512 MB",
        "1024 MB",
        "1536 MB",
        "2048 MB",
        "3008 MB",
        "4096 MB",
        "5120 MB",
        "6144 MB",
        "7168 MB",
        "8192 MB",
        "9216 MB",
        "10240 MB",
    ],
    "architecture": ["x86_64", "arm64"],
}

# Recursos ElastiCache
ELASTICACHE_RESOURCES = {
    "cacheNodeTypes": [
        "cache.t3.micro",
        "cache.t3.small",
        "cache.t3.medium",
        "cache.m5.large",
        "cache.m5.xlarge",
        "cache.m5.2xlarge",
        "cache.m5.4xlarge",
        "cache.m5.12xlarge",
        "cache.m5.24xlarge",
        "cache.r5.large",
        "cache.r5.xlarge",
        "cache.r5.2xlarge",
        "cache.r5.4xlarge",
        "cache.r5.12xlarge",
        "cache.r5.24xlarge",
        "cache.m6g.large",
        "cache.m6g.xlarge",
        "cache.m6g.2xlarge",
        "cache.m6g.4xlarge",
        "cache.m6g.8xlarge",
        "cache.m6g.12xlarge",
        "cache.m6g.16xlarge",
        "cache.r6g.large",
        "cache.r6g.xlarge",
        "cache.r6g.2xlarge",
        "cache.r6g.4xlarge",
        "cache.r6g.8xlarge",
        "cache.r6g.12xlarge",
        "cache.r6g.16xlarge",
    ],
    "engines": ["redis", "memcached"],
}

# Recursos OpenSearch
OPENSEARCH_RESOURCES = {
    "instanceTypes": [
        "t3.small.search",
        "t3.medium.search",
        "m5.large.search",
        "m5.xlarge.search",
        "m5.2xlarge.search",
        "m5.4xlarge.search",
        "m5.12xlarge.search",
        "c5.large.search",
        "c5.xlarge.search",
        "c5.2xlarge.search",
        "c5.4xlarge.search",
        "c5.9xlarge.search",
        "c5.18xlarge.search",
        "r5.large.search",
        "r5.xlarge.search",
        "r5.2xlarge.search",
        "r5.4xlarge.search",
        "r5.12xlarge.search",
    ],
    "storageTypes": ["EBS", "Instance"],
    "deploymentOptions": ["Single-AZ", "Multi-AZ"],
}

# Recursos CloudWatch
CLOUDWATCH_RESOURCES = {
    "metrics": ["Basic", "Detailed"],
    "alarms": ["Standard", "High Resolution"],
    "logs": ["Ingested", "Stored", "Analyzed"],
    "dashboards": ["Standard"],
}

# Recursos ECR
ECR_RESOURCES = {"storage": ["Standard"], "dataTransfer": ["Internet", "VPC"]}

# Recursos Route 53
ROUTE53_RESOURCES = {
    "hostedZoneTypes": ["Public", "Private"],
    "recordTypes": ["A", "AAAA", "CNAME", "MX", "NS", "PTR", "SOA", "SRV", "TXT"],
    "routingPolicies": [
        "Simple",
        "Weighted",
        "Latency",
        "Failover",
        "Geolocation",
        "Geoproximity",
        "Multivalue",
    ],
}


def generate_ec2_instance_list():
    """Gera uma lista plana de todas as instâncias EC2"""
    instances = []

    for family, family_instances in EC2_INSTANCES.items():
        for instance in family_instances:
            instance_data = instance.copy()
            instance_data["family"] = family
            instances.append(instance_data)

    return instances


def get_ec2_instance_types():
    """Retorna uma lista com todos os tipos de instâncias EC2"""
    instance_types = []

    for family_instances in EC2_INSTANCES.values():
        for instance in family_instances:
            instance_types.append(instance["type"])

    return sorted(instance_types)


def get_s3_storage_classes():
    """Retorna as classes de armazenamento S3"""
    return S3_STORAGE_CLASSES


def get_elasticache_node_types():
    """Retorna os tipos de nó do ElastiCache"""
    return ELASTICACHE_RESOURCES["cacheNodeTypes"]


def get_lambda_configurations():
    """Retorna as configurações do Lambda"""
    return LAMBDA_RESOURCES


def get_fargate_resources():
    """Retorna os recursos do Fargate"""
    return FARGATE_RESOURCES


def get_opensearch_resources():
    """Retorna os recursos do OpenSearch"""
    return OPENSEARCH_RESOURCES


def create_mock_ec2_pricing_data():
    """
    Cria dados de preço simulados para EC2, no mesmo formato retornado pela API de pricing
    """
    mock_products = []
    regions = ["us-east-1", "us-west-2", "eu-west-1", "sa-east-1"]
    os_options = ["Linux", "Windows"]

    for family, instances in EC2_INSTANCES.items():
        for instance in instances:
            for region in regions:
                for os_type in os_options:
                    # Preço base por hora: simples multiplicador baseado no número de vCPUs
                    base_price = instance["vcpu"] * 0.0052  # $0.0052 por vCPU

                    # Ajusta preço para Windows
                    if os_type == "Windows":
                        base_price *= 1.3

                    # Ajusta preço para região
                    if region == "us-west-2":
                        base_price *= 1.05
                    elif region == "eu-west-1":
                        base_price *= 1.1
                    elif region == "sa-east-1":
                        base_price *= 1.25

                    product = {
                        "serviceCode": "AmazonEC2",
                        "attributes": {
                            "instanceType": instance["type"],
                            "operatingSystem": os_type,
                            "location": region,
                            "vcpu": str(instance["vcpu"]),
                            "memory": instance["memory"],
                            "instanceFamily": family,
                        },
                        "terms": {"OnDemand": {"price": str(round(base_price, 4))}},
                    }
                    mock_products.append(product)

    return mock_products


def mock_aws_pricing(service_code):
    """
    Simula a API de pricing da AWS para quando não há credenciais disponíveis
    """
    if service_code == "AmazonEC2":
        return create_mock_ec2_pricing_data()
    # Outros serviços podem ser adicionados conforme necessário
    return []
