from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

from .aws_services import (
    get_aws_pricing,
    get_all_ec2_instance_types,
    estimate_price,
    get_ec2_price,
)

router = APIRouter()


@router.get("/")
def read_root():
    return {"message": "AWS Price Calculator API"}


@router.get("/ec2/instances", response_model=List[str])
def get_ec2_instances():
    """
    Obtém todos os tipos de instâncias EC2 disponíveis, usando dados da API ou estáticos
    """
    return get_all_ec2_instance_types()


@router.get("/pricing/{service_code}")
def get_pricing(
    service_code: str,
    region: Optional[str] = None,
    instance_type: Optional[str] = None,
    os: Optional[str] = None,
    max_results: int = Query(100, gt=0, le=1000),
):
    """
    Obtém informações de preços para um serviço específico da AWS.
    """
    filters = []

    if region:
        filters.append({"Type": "TERM_MATCH", "Field": "regionCode", "Value": region})

    if instance_type:
        filters.append(
            {"Type": "TERM_MATCH", "Field": "instanceType", "Value": instance_type}
        )

    if os:
        filters.append({"Type": "TERM_MATCH", "Field": "operatingSystem", "Value": os})

    return get_aws_pricing(service_code, filters, max_results)


class EstimateParams(BaseModel):
    service: str
    params: Dict[str, Any]


@router.post("/estimate")
def create_estimate(data: EstimateParams):
    """
    Estima o preço de um serviço AWS baseado nos parâmetros fornecidos.
    """
    return estimate_price(data.service, data.params)


@router.get("/ec2/price")
def calculate_ec2_price(
    instance_type: str,
    region: str = "us-east-1",
    os: str = "Linux",
    hours_per_month: float = 730,  # 24h * ~30.4 days
):
    """
    Calcula o preço mensal de uma instância EC2.
    """
    return get_ec2_price(instance_type, region, os, hours_per_month)
