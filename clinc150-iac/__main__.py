"""An AWS Python Pulumi program to create EKS and deploy CLINC150 app."""

import pulumi
import pulumi_aws as aws
import pulumi_eks as eks
import pulumi_kubernetes as k8s
from pulumi_kubernetes.yaml import ConfigGroup

# ==========================================================
# FASE 1: RED Y SUBNETS (para evitar zonas no soportadas)
# ==========================================================

# Crear una VPC simple
vpc = aws.ec2.Vpc(
    "clinc150-vpc",
    cidr_block="10.0.0.0/16",
    enable_dns_hostnames=True,
    enable_dns_support=True,
    tags={"Name": "clinc150-vpc"},
)

# Subnets públicas en AZs válidas
subnet_a = aws.ec2.Subnet(
    "clinc150-subnet-a",
    vpc_id=vpc.id,
    cidr_block="10.0.1.0/24",
    availability_zone="us-east-1a",
    map_public_ip_on_launch=True,
)

subnet_b = aws.ec2.Subnet(
    "clinc150-subnet-b",
    vpc_id=vpc.id,
    cidr_block="10.0.2.0/24",
    availability_zone="us-east-1b",
    map_public_ip_on_launch=True,
)

subnet_c = aws.ec2.Subnet(
    "clinc150-subnet-c",
    vpc_id=vpc.id,
    cidr_block="10.0.3.0/24",
    availability_zone="us-east-1c",
    map_public_ip_on_launch=True,
)

# Gateway de Internet y ruta para acceso externo
igw = aws.ec2.InternetGateway("clinc150-igw", vpc_id=vpc.id)
route_table = aws.ec2.RouteTable(
    "clinc150-rt",
    vpc_id=vpc.id,
    routes=[aws.ec2.RouteTableRouteArgs(cidr_block="0.0.0.0/0", gateway_id=igw.id)],
)
for subnet in [subnet_a, subnet_b, subnet_c]:
    aws.ec2.RouteTableAssociation(
        f"{subnet._name}-assoc",
        subnet_id=subnet.id,
        route_table_id=route_table.id,
    )

# ==========================================================
# FASE 2: CLÚSTER EKS (Optimizado para Free Tier)
# ==========================================================

cluster = eks.Cluster(
    "clinc150-eks-cluster",
    version="1.28",
    instance_type="t3.small",   # Instancia económica
    desired_capacity=1,         # Solo 1 nodo inicial
    min_size=1,
    max_size=3,
    vpc_id=vpc.id,
    subnet_ids=[subnet_a.id, subnet_b.id, subnet_c.id],
    tags={"Project": "CLINC150-IAC"},
)

# ==========================================================
# FASE 3: PROVEEDOR DE KUBERNETES
# ==========================================================

k8s_provider = k8s.Provider(
    "k8s-provider",
    kubeconfig=cluster.kubeconfig,
)

# ==========================================================
# FASE 4: DESPLIEGUE DE MANIFIESTOS KUBERNETES
# ==========================================================

# 1️⃣ Base de Datos (PVC y Deployment)
db_resources = ConfigGroup(
    "db-resources",
    files=["kubernetes/db-pvc.yaml", "kubernetes/db.yaml"],
    opts=pulumi.ResourceOptions(provider=k8s_provider),
)

# 2️⃣ Carga de Datos (Job)
data_loader = ConfigGroup(
    "data-loader-job",
    files=["kubernetes/data-loader-job.yaml"],
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[db_resources]),
)

# 3️⃣ Backend, Frontend y Autoescalado
app_resources = ConfigGroup(
    "app-resources",
    files=[
        "kubernetes/backend.yaml",
        "kubernetes/frontend.yaml",
        "kubernetes/hpa-backend.yaml",
        "kubernetes/hpa-frontend.yaml",
    ],
    opts=pulumi.ResourceOptions(provider=k8s_provider, depends_on=[data_loader]),
)

# ==========================================================
# FASE 5: EXPORTAR INFORMACIÓN
# ==========================================================

pulumi.export("vpc_id", vpc.id)
pulumi.export("subnets", [subnet_a.id, subnet_b.id, subnet_c.id])
pulumi.export("cluster_name", cluster.core.cluster.name)
pulumi.export("kubeconfig", cluster.kubeconfig)

def get_frontend_url(resources):
    # Buscar el Service 'frontend-service' dentro del ConfigGroup
    for r in resources:
        if r['kind'] == 'Service' and r['metadata']['name'] == 'frontend-service':
            status = r.get('status', {})
            ingress = status.get('load_balancer', {}).get('ingress', [])
            if ingress and ingress[0].get('hostname'):
                return ingress[0]['hostname']
    return "Pending"

pulumi.export(
    "frontend_url",
    app_resources.resources.apply(lambda resources: get_frontend_url(resources))
)
