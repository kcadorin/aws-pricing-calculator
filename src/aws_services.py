import boto3
from decimal import Decimal
import json
import os
import logging
from aws_static_resources import (
    mock_aws_pricing,
    get_ec2_instance_types,
)  # Import static data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Class to convert Decimal to float (for serialization)
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


# Function to get prices from the API
def get_aws_pricing(service_code, filters=None, max_results=100):
    """
    Obtém preços da API da AWS, ou usa dados estáticos se não houver credenciais disponíveis.

    Args:
        service_code: Código do serviço AWS (ex: AmazonEC2)
        filters: Lista de filtros para a API
        max_results: Número máximo de resultados a retornar

    Returns:
        Lista de produtos com detalhes de preço
    """
    if filters is None:
        filters = []

    try:
        # Tentar conectar à API da AWS
        pricing_client = boto3.client("pricing", region_name="us-east-1")

        # Get available services
        response = pricing_client.get_products(
            ServiceCode=service_code, Filters=filters, MaxResults=max_results
        )

        products = []
        for price_item in response["PriceList"]:
            products.append(json.loads(price_item))

        logger.info(
            f"Obtidos {len(products)} produtos da API de pricing para {service_code}"
        )
        return products
    except Exception as e:
        # Se houver erro (como credenciais ausentes), usar dados estáticos
        logger.warning(
            f"Erro ao acessar a API de pricing: {str(e)}. Usando dados estáticos."
        )
        return mock_aws_pricing(service_code)


# Function to get EC2 instance types (combining API and static data)
def get_all_ec2_instance_types():
    """
    Retorna uma lista completa de tipos de instância EC2, combinando dados da API e estáticos
    """
    # Primeiro tenta obter da API
    try:
        api_instances = get_ec2_instances_from_api()
        if api_instances and len(api_instances) > 0:
            return api_instances
    except Exception as e:
        logger.warning(f"Não foi possível obter tipos de instância da API: {str(e)}")

    # Se a API falhar, usa dados estáticos
    return get_ec2_instance_types()


def get_ec2_instances_from_api():
    """
    Tenta obter tipos de instância EC2 da API
    """
    products = get_aws_pricing("AmazonEC2")

    if isinstance(products, dict) and "error" in products:
        return []

    # Conjunto para armazenar tipos únicos de instâncias
    instance_types = set()

    # Extrair tipos de instâncias dos produtos retornados
    for product in products:
        if "attributes" in product and "instanceType" in product["attributes"]:
            instance_types.add(product["attributes"]["instanceType"])

    return sorted(list(instance_types))


# Generic function to estimate prices
def estimate_price(service, params):
    """
    Estimates the price of an AWS service based on parameters.

    This function uses approximate prices for a quick estimate.
    In a complete implementation, these prices would be obtained via API.
    """
    if service == "EC2":
        return estimate_ec2(params)
    elif service == "S3":
        return estimate_s3(params)
    elif service == "Lambda":
        return estimate_lambda(params)
    elif service == "Fargate/ECS":
        return estimate_fargate(params)
    elif service == "CloudWatch":
        return estimate_cloudwatch(params)
    elif service == "ElastiCache":
        return estimate_elasticache(params)
    elif service == "ECR":
        return estimate_ecr(params)
    elif service == "OpenSearch":
        return estimate_opensearch(params)
    elif service == "Route 53":
        return estimate_route53(params)
    else:
        return {"error": "Service not supported"}


# Estimated prices for EC2 (prices per hour)
EC2_PRICES = {
    "t3.micro": {
        "us-east-1": 0.0104,
        "us-west-2": 0.0104,
        "eu-west-1": 0.0114,
        "sa-east-1": 0.0208,
    },
    "t3.small": {
        "us-east-1": 0.0208,
        "us-west-2": 0.0208,
        "eu-west-1": 0.0228,
        "sa-east-1": 0.0416,
    },
    "t3.medium": {
        "us-east-1": 0.0416,
        "us-west-2": 0.0416,
        "eu-west-1": 0.0456,
        "sa-east-1": 0.0832,
    },
    "m5.large": {
        "us-east-1": 0.096,
        "us-west-2": 0.096,
        "eu-west-1": 0.106,
        "sa-east-1": 0.192,
    },
    "c5.large": {
        "us-east-1": 0.085,
        "us-west-2": 0.085,
        "eu-west-1": 0.094,
        "sa-east-1": 0.17,
    },
}

# Price multiplier for Windows
WINDOWS_MULTIPLIER = 1.3


def estimate_ec2(params):
    """
    Estimates the price of EC2 instances.

    params: dict with:
        - instance_type: instance type
        - region: AWS region
        - os_type: operating system
        - quantity: number of instances
        - hours_per_day: hours per day
        - days_per_month: days per month
    """
    instance_type = params.get("instance_type", "t3.micro")
    region = params.get("region", "us-east-1")
    os_type = params.get("os_type", "Linux")
    quantity = params.get("quantity", 1)
    hours_per_day = params.get("hours_per_day", 24)
    days_per_month = params.get("days_per_month", 30)

    base_price = EC2_PRICES.get(instance_type, {}).get(
        region, 0.0416
    )  # default price if not found

    # Apply multiplier for Windows
    if os_type == "Windows":
        base_price *= WINDOWS_MULTIPLIER

    monthly_hours = hours_per_day * days_per_month
    total_cost = base_price * quantity * monthly_hours

    return {
        "unit_price": base_price,
        "quantity": quantity,
        "monthly_hours": monthly_hours,
        "total_price": total_cost,
    }


# Estimated prices for S3 (price per GB per month)
S3_PRICES = {
    "Standard": {
        "us-east-1": 0.023,
        "us-west-2": 0.023,
        "eu-west-1": 0.024,
        "sa-east-1": 0.0405,
    },
    "Intelligent-Tiering": {
        "us-east-1": 0.025,
        "us-west-2": 0.025,
        "eu-west-1": 0.026,
        "sa-east-1": 0.0435,
    },
    "Standard-IA": {
        "us-east-1": 0.0125,
        "us-west-2": 0.0125,
        "eu-west-1": 0.0131,
        "sa-east-1": 0.0216,
    },
    "One Zone-IA": {
        "us-east-1": 0.01,
        "us-west-2": 0.01,
        "eu-west-1": 0.0104,
        "sa-east-1": 0.0172,
    },
    "Glacier": {
        "us-east-1": 0.004,
        "us-west-2": 0.004,
        "eu-west-1": 0.0042,
        "sa-east-1": 0.0069,
    },
    "Glacier Deep Archive": {
        "us-east-1": 0.00099,
        "us-west-2": 0.00099,
        "eu-west-1": 0.00104,
        "sa-east-1": 0.00171,
    },
}


def estimate_s3(params):
    """
    Estimates the price of S3 storage.

    params: dict with:
        - storage_gb: amount of storage in GB
        - storage_class: storage class
        - region: AWS region
    """
    storage_gb = params.get("storage_gb", 100)
    storage_class = params.get("storage_class", "Standard")
    region = params.get("region", "us-east-1")

    base_price = S3_PRICES.get(storage_class, {}).get(
        region, 0.023
    )  # default price if not found
    total_cost = base_price * storage_gb

    return {
        "unit_price": base_price,
        "quantity": storage_gb,
        "monthly_hours": 1,  # Not relevant for S3
        "total_price": total_cost,
    }


# Estimated prices for Lambda (per million requests and per GB-second)
LAMBDA_PRICES = {
    "requests": {
        "us-east-1": 0.20,
        "us-west-2": 0.20,
        "eu-west-1": 0.20,
        "sa-east-1": 0.20,
    },
    "duration": {
        "us-east-1": 0.0000166667,
        "us-west-2": 0.0000166667,
        "eu-west-1": 0.0000166667,
        "sa-east-1": 0.0000166667,
    },
}


def estimate_lambda(params):
    """
    Estimates the price of Lambda functions.

    params: dict with:
        - requests: number of requests per month (in millions)
        - memory: function memory in MB
        - avg_duration: average function duration in ms
        - region: AWS region
    """
    requests_millions = params.get("requests", 1)
    memory_mb = params.get("memory", 128)
    avg_duration_ms = params.get("avg_duration", 100)
    region = params.get("region", "us-east-1")

    # Calculate GB-seconds
    gb_factor = memory_mb / 1024  # Convert MB to GB
    seconds_per_invocation = avg_duration_ms / 1000  # Convert ms to seconds
    total_seconds = requests_millions * 1000000 * seconds_per_invocation
    gb_seconds = total_seconds * gb_factor

    # Calculate costs
    request_price = LAMBDA_PRICES.get("requests", {}).get(region, 0.20)
    duration_price = LAMBDA_PRICES.get("duration", {}).get(region, 0.0000166667)

    request_cost = request_price * requests_millions
    duration_cost = duration_price * gb_seconds

    total_cost = request_cost + duration_cost

    return {
        "unit_price": duration_price,  # Price per GB-second
        "quantity": gb_seconds,  # Total GB-seconds
        "requests_cost": request_cost,
        "total_price": total_cost,
    }


# Estimated prices for Fargate (per vCPU per hour and per GB of memory per hour)
FARGATE_PRICES = {
    "vcpu": {
        "us-east-1": 0.04048,
        "us-west-2": 0.04048,
        "eu-west-1": 0.04452,
        "sa-east-1": 0.04856,
    },
    "memory": {
        "us-east-1": 0.004445,
        "us-west-2": 0.004445,
        "eu-west-1": 0.004889,
        "sa-east-1": 0.005334,
    },
}


def estimate_fargate(params):
    """
    Estimates the price of Fargate.

    params: dict with:
        - vcpu: number of vCPUs
        - memory_gb: amount of memory in GB
        - hours_per_month: hours per month of usage
        - region: AWS region
    """
    vcpu = params.get("vcpu", 1)
    memory_gb = params.get("memory_gb", 2)
    hours_per_month = params.get("hours_per_month", 730)  # ~30 days
    region = params.get("region", "us-east-1")

    vcpu_price = FARGATE_PRICES.get("vcpu", {}).get(region, 0.04048)
    memory_price = FARGATE_PRICES.get("memory", {}).get(region, 0.004445)

    vcpu_cost = vcpu_price * vcpu * hours_per_month
    memory_cost = memory_price * memory_gb * hours_per_month

    total_cost = vcpu_cost + memory_cost

    # Calculating unit price per hour (vcpu + memory)
    unit_price = (vcpu_price * vcpu) + (memory_price * memory_gb)

    return {
        "unit_price": unit_price,
        "quantity": hours_per_month,
        "vcpu_cost": vcpu_cost,
        "memory_cost": memory_cost,
        "total_price": total_cost,
    }


# Functions for other services
def estimate_cloudwatch(params):
    """
    Basic simulation for CloudWatch.

    In a real implementation, it would be necessary to consider various factors:
    - Logs (ingestion and storage)
    - Metrics (basic and custom)
    - Alarms
    - Dashboards
    """
    ingestion_gb = params.get("ingestion_gb", 10)
    storage_gb = params.get("storage_gb", 10)
    metrics = params.get("metrics", 10)
    alarms = params.get("alarms", 5)
    dashboards = params.get("dashboards", 1)

    # Approximate prices
    ingestion_price = 0.50  # per GB
    storage_price = 0.03  # per GB-month
    metrics_price = 0.30  # per metric per month
    alarm_price = 0.10  # per alarm per month
    dashboard_price = 3.00  # per dashboard per month

    total_cost = (
        (ingestion_gb * ingestion_price)
        + (storage_gb * storage_price)
        + (metrics * metrics_price)
        + (alarms * alarm_price)
        + (dashboards * dashboard_price)
    )

    return {
        "unit_price": 1.0,  # There is no simple unit price for CloudWatch
        "quantity": 1,
        "total_price": total_cost,
    }


def estimate_elasticache(params):
    """
    Estimate for ElastiCache (Redis).
    """
    node_type = params.get("node_type", "cache.t3.micro")
    nodes = params.get("nodes", 1)
    hours = params.get("hours", 730)  # ~30 days
    region = params.get("region", "us-east-1")

    # Approximate prices per hour for different node types (us-east-1)
    node_prices = {
        "cache.t3.micro": 0.018,
        "cache.t3.small": 0.036,
        "cache.t3.medium": 0.074,
        "cache.m5.large": 0.156,
        "cache.r5.large": 0.216,
    }

    # Adjust price for region
    region_multipliers = {
        "us-east-1": 1.0,
        "us-west-2": 1.0,
        "eu-west-1": 1.1,
        "sa-east-1": 1.25,
    }

    base_price = node_prices.get(node_type, 0.018)
    region_multiplier = region_multipliers.get(region, 1.0)

    unit_price = base_price * region_multiplier
    total_cost = unit_price * nodes * hours

    return {
        "unit_price": unit_price,
        "quantity": nodes * hours,
        "total_price": total_cost,
    }


def estimate_ecr(params):
    """
    Estimate for ECR.
    """
    storage_gb = params.get("storage_gb", 10)
    data_transfer_gb = params.get("data_transfer_gb", 50)

    # Approximate prices
    storage_price = 0.10  # per GB-month
    data_transfer_price = 0.09  # per GB

    storage_cost = storage_gb * storage_price
    data_transfer_cost = data_transfer_gb * data_transfer_price

    total_cost = storage_cost + data_transfer_cost

    return {
        "unit_price": storage_price,
        "quantity": storage_gb,
        "data_transfer_cost": data_transfer_cost,
        "total_price": total_cost,
    }


def estimate_opensearch(params):
    """
    Estimate for OpenSearch.
    """
    instance_type = params.get("instance_type", "t3.small.search")
    instances = params.get("instances", 1)
    storage_gb = params.get("storage_gb", 10)
    hours = params.get("hours", 730)  # ~30 days
    region = params.get("region", "us-east-1")

    # Approximate prices per hour for different instance types (us-east-1)
    instance_prices = {
        "t3.small.search": 0.036,
        "t3.medium.search": 0.073,
        "m5.large.search": 0.139,
        "c5.large.search": 0.123,
    }

    # Storage price per GB-month
    storage_price = 0.135

    # Adjust price for region
    region_multipliers = {
        "us-east-1": 1.0,
        "us-west-2": 1.0,
        "eu-west-1": 1.1,
        "sa-east-1": 1.25,
    }

    base_price = instance_prices.get(instance_type, 0.036)
    region_multiplier = region_multipliers.get(region, 1.0)

    instance_unit_price = base_price * region_multiplier
    instance_cost = instance_unit_price * instances * hours
    storage_cost = storage_price * storage_gb

    total_cost = instance_cost + storage_cost

    return {
        "unit_price": instance_unit_price,
        "quantity": instances * hours,
        "storage_cost": storage_cost,
        "total_price": total_cost,
    }


def estimate_route53(params):
    """
    Estimate for Route 53.
    """
    hosted_zones = params.get("hosted_zones", 1)
    queries_millions = params.get("queries_millions", 1)

    # Approximate prices
    zone_price = 0.50  # per hosted zone per month
    query_price = 0.40  # per million queries

    zone_cost = hosted_zones * zone_price
    query_cost = queries_millions * query_price

    total_cost = zone_cost + query_cost

    return {
        "unit_price": zone_price,
        "quantity": hosted_zones,
        "query_cost": query_cost,
        "total_price": total_cost,
    }


def get_ec2_price(
    instance_type: str,
    region: str = "us-east-1",
    os: str = "Linux",
    hours_per_month: float = 730,
) -> dict:
    """
    Calcula o preço mensal de uma instância EC2.
    Se não conseguir acessar a API da AWS, usa dados estáticos.

    Args:
        instance_type: Tipo de instância EC2 (ex: t2.micro)
        region: Região AWS (default: us-east-1)
        os: Sistema operacional (default: Linux)
        hours_per_month: Horas de uso por mês (default: 730)

    Returns:
        dict: Informações de preço com custo mensal estimado
    """
    try:
        filters = [
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type},
            {"Type": "TERM_MATCH", "Field": "regionCode", "Value": region},
            {"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": os},
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
        ]

        products = get_aws_pricing("AmazonEC2", filters)

        if not products:
            raise ValueError(
                f"Nenhum produto encontrado para a instância {instance_type}"
            )

        product = products[0]
        price_per_hour = float(product.get("onDemandPrice", 0))

        return {
            "instance_type": instance_type,
            "region": region,
            "operating_system": os,
            "price_per_hour": price_per_hour,
            "hours_per_month": hours_per_month,
            "monthly_cost": price_per_hour * hours_per_month,
            "source": "aws_api",
        }
    except Exception as e:
        logging.warning(
            f"Erro ao obter preço via API: {str(e)}. Usando dados estáticos."
        )

        # Usar dados estáticos de mock
        from static.mock_aws_pricing import EC2_PRICE_DATA

        # Procurar o preço nos dados estáticos
        price_key = f"{region}:{instance_type}:{os}"
        if price_key in EC2_PRICE_DATA:
            price_per_hour = EC2_PRICE_DATA[price_key]
            return {
                "instance_type": instance_type,
                "region": region,
                "operating_system": os,
                "price_per_hour": price_per_hour,
                "hours_per_month": hours_per_month,
                "monthly_cost": price_per_hour * hours_per_month,
                "source": "static_data",
            }
        else:
            # Se não encontrar dados específicos, usar um cálculo aproximado baseado
            # no tipo de instância (isso é uma simplificação)
            price_per_hour = 0.0

            # Extrai o tipo de instância (t2, m5, etc)
            instance_family = instance_type.split(".")[0]
            instance_size = instance_type.split(".")[1]

            # Preços base aproximados por família (muito simplificado)
            base_prices = {
                "t2": 0.0116,
                "t3": 0.0104,
                "t4g": 0.0084,
                "m5": 0.096,
                "m6g": 0.077,
                "m6i": 0.096,
                "c5": 0.085,
                "c6g": 0.068,
                "c6i": 0.085,
                "r5": 0.126,
                "r6g": 0.101,
                "r6i": 0.126,
                "x2": 3.97,
                "z1d": 0.24,
                # Adicione mais famílias conforme necessário
            }

            # Multiplicadores de tamanho
            size_multipliers = {
                "nano": 0.25,
                "micro": 0.5,
                "small": 1,
                "medium": 2,
                "large": 4,
                "xlarge": 8,
                "2xlarge": 16,
                "4xlarge": 32,
                "8xlarge": 64,
                "16xlarge": 128,
                "32xlarge": 256,
            }

            # Obter preço base para a família ou usar um valor padrão
            base_price = base_prices.get(instance_family, 0.05)

            # Obter multiplicador para o tamanho ou usar um valor padrão
            multiplier = 1
            for size_name, size_value in size_multipliers.items():
                if size_name in instance_size:
                    multiplier = size_value
                    break

            # Calcular preço aproximado
            price_per_hour = base_price * multiplier

            return {
                "instance_type": instance_type,
                "region": region,
                "operating_system": os,
                "price_per_hour": price_per_hour,
                "hours_per_month": hours_per_month,
                "monthly_cost": price_per_hour * hours_per_month,
                "source": "estimated_data",
                "note": "Preço estimado baseado no tipo de instância, pode não ser preciso",
            }
