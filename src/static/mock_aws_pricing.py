"""
Dados estáticos de preços para instâncias EC2 da AWS.
Este arquivo contém preços aproximados para fins de cálculo quando a API não está disponível.
Formato da chave: "região:tipo_instância:sistema_operacional"
Valores em USD por hora.
"""

# Preços de instâncias EC2 (aproximados)
EC2_PRICE_DATA = {
    # us-east-1 (N. Virginia)
    "us-east-1:t2.micro:Linux": 0.0116,
    "us-east-1:t2.small:Linux": 0.023,
    "us-east-1:t2.medium:Linux": 0.0464,
    "us-east-1:t2.large:Linux": 0.0928,
    "us-east-1:t3.micro:Linux": 0.0104,
    "us-east-1:t3.small:Linux": 0.0208,
    "us-east-1:t3.medium:Linux": 0.0416,
    "us-east-1:m5.large:Linux": 0.096,
    "us-east-1:m5.xlarge:Linux": 0.192,
    "us-east-1:m5.2xlarge:Linux": 0.384,
    "us-east-1:c5.large:Linux": 0.085,
    "us-east-1:c5.xlarge:Linux": 0.17,
    "us-east-1:r5.large:Linux": 0.126,
    "us-east-1:r5.xlarge:Linux": 0.252,
    # Windows preços
    "us-east-1:t2.micro:Windows": 0.0162,
    "us-east-1:t2.medium:Windows": 0.0644,
    "us-east-1:m5.large:Windows": 0.192,
    # us-west-2 (Oregon)
    "us-west-2:t2.micro:Linux": 0.0116,
    "us-west-2:t2.medium:Linux": 0.0464,
    "us-west-2:m5.large:Linux": 0.096,
    "us-west-2:c5.large:Linux": 0.085,
    # eu-west-1 (Irlanda)
    "eu-west-1:t2.micro:Linux": 0.0126,
    "eu-west-1:t2.medium:Linux": 0.0504,
    "eu-west-1:m5.large:Linux": 0.107,
    "eu-west-1:c5.large:Linux": 0.097,
    # sa-east-1 (São Paulo)
    "sa-east-1:t2.micro:Linux": 0.0181,
    "sa-east-1:t2.small:Linux": 0.0362,
    "sa-east-1:t2.medium:Linux": 0.0724,
    "sa-east-1:t3.micro:Linux": 0.0162,
    "sa-east-1:t3.small:Linux": 0.0324,
    "sa-east-1:t3.medium:Linux": 0.0648,
    "sa-east-1:m5.large:Linux": 0.148,
    "sa-east-1:c5.large:Linux": 0.13,
    "sa-east-1:r5.large:Linux": 0.196,
}

# Regiões AWS
AWS_REGIONS = [
    "us-east-1",  # Leste dos EUA (Norte da Virgínia)
    "us-east-2",  # Leste dos EUA (Ohio)
    "us-west-1",  # Oeste dos EUA (Norte da Califórnia)
    "us-west-2",  # Oeste dos EUA (Oregon)
    "af-south-1",  # África (Cidade do Cabo)
    "ap-east-1",  # Ásia-Pacífico (Hong Kong)
    "ap-south-1",  # Ásia-Pacífico (Mumbai)
    "ap-northeast-1",  # Ásia-Pacífico (Tóquio)
    "ap-northeast-2",  # Ásia-Pacífico (Seul)
    "ap-northeast-3",  # Ásia-Pacífico (Osaka)
    "ap-southeast-1",  # Ásia-Pacífico (Singapura)
    "ap-southeast-2",  # Ásia-Pacífico (Sydney)
    "ca-central-1",  # Canadá (Central)
    "eu-central-1",  # Europa (Frankfurt)
    "eu-west-1",  # Europa (Irlanda)
    "eu-west-2",  # Europa (Londres)
    "eu-west-3",  # Europa (Paris)
    "eu-north-1",  # Europa (Estocolmo)
    "eu-south-1",  # Europa (Milão)
    "me-south-1",  # Oriente Médio (Bahrein)
    "sa-east-1",  # América do Sul (São Paulo)
]

# Sistemas operacionais suportados
OPERATING_SYSTEMS = [
    "Linux",
    "Windows",
    "RHEL",
    "SUSE",
    "Linux with SQL Std",
    "Linux with SQL Web",
    "Linux with SQL Ent",
    "Windows with SQL Std",
    "Windows with SQL Web",
    "Windows with SQL Ent",
]
