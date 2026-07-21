# AIOps Platform - Terraform Infrastructure
terraform {
  required_version = ">= 1.7.0"
  
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.34"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.16"
    }
  }

  backend "s3" {
    bucket = "aiops-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}

variable "environment" {
  type    = string
  default = "staging"
}

variable "cluster_name" {
  type    = string
  default = "aiops-cluster"
}

variable "node_count" {
  type    = number
  default = 3
}

# ─── Kubernetes Cluster ─────────────────────────────────────────────
module "networking" {
  source = "./modules/networking"
  
  environment  = var.environment
  cluster_name = var.cluster_name
}

module "compute" {
  source = "./modules/compute"
  
  environment  = var.environment
  cluster_name = var.cluster_name
  node_count   = var.node_count
  subnet_ids   = module.networking.subnet_ids
}

module "storage" {
  source = "./modules/storage"
  
  environment = var.environment
}

# ─── Helm Releases ──────────────────────────────────────────────────
resource "helm_release" "prometheus" {
  name       = "prometheus"
  namespace  = "monitoring"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  version    = "65.0.0"

  set {
    name  = "grafana.enabled"
    value = "true"
  }

  set {
    name  = "alertmanager.enabled"
    value = "true"
  }
}

resource "helm_release" "loki" {
  name       = "loki"
  namespace  = "monitoring"
  repository = "https://grafana.github.io/helm-charts"
  chart      = "loki-stack"
  version    = "2.10.0"
}

resource "helm_release" "redis" {
  name       = "redis"
  namespace  = "aiops"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "redis"
  version    = "20.0.0"

  set {
    name  = "auth.password"
    value = var.redis_password
  }
}

resource "helm_release" "rabbitmq" {
  name       = "rabbitmq"
  namespace  = "aiops"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "rabbitmq"
  version    = "15.0.0"
}

resource "helm_release" "postgresql" {
  name       = "postgresql"
  namespace  = "aiops"
  repository = "https://charts.bitnami.com/bitnami"
  chart      = "postgresql"
  version    = "16.0.0"

  set {
    name  = "auth.database"
    value = "aiops"
  }

  set {
    name  = "primary.persistence.size"
    value = "50Gi"
  }
}

variable "redis_password" {
  type      = string
  sensitive = true
}

output "cluster_endpoint" {
  value = module.compute.cluster_endpoint
}
