# k8s Helm App — Todo App on k3s

> 🇺🇦 [Українська версія](README.uk.md)

Full-stack **Todo application** deployed on a single-node **k3s** cluster using **Helm charts**.
Demonstrates production DevOps practices: parameterised Helm packaging, TLS via cert-manager,
observability stack (Prometheus + Grafana + Loki), automated backups, and Helm hooks.

## Stack

| Layer | Technology |
|---|---|
| Kubernetes | k3s v1.34+ |
| Ingress | Traefik (built-in k3s) |
| TLS | cert-manager + Let's Encrypt |
| Package Manager | Helm v3 |
| Backend | Python Flask — `vladdisslav/todo-backend:v1.0.0` |
| Frontend | Nginx + HTML |
| Database | MySQL 8.0 |
| Monitoring | Prometheus, Grafana, Loki, Promtail, Blackbox, Node Exporter |
| Backup | Kubernetes CronJob → PVC (daily mysqldump) |

## Architecture

```
         Internet
             │
    ┌───────┴───────┐
    │   Traefik     │  :80/:443
    │ + cert-manager│
    └───────┬───────┘
             │
    ┌───────┴───────┐
    │   Frontend   │
    └───────┬───────┘
             │ /api
    ┌───────┴───────┐
    │   Backend    │  x2 replicas
    └───────┬───────┘
             │
    ┌───────┴───────┐
    │  MySQL 8.0   │  PVC
    └───────────────┘
```

## Repository Structure

```
.
├── backend/
│   ├── app.py              ← Flask REST API
│   ├── Dockerfile
│   └── requirements.txt
├── helm-charts/
│   ├── backend/            ← Deployment, Service, Secret, post-install Hook
│   ├── frontend/           ← Deployment, Service
│   ├── database/           ← StatefulSet, PVC, Secret
│   ├── ingress/            ← Traefik IngressRoute, cert-manager Certificate
│   ├── backup/             ← CronJob (daily mysqldump → PVC)
│   └── monitoring/         ← Prometheus, Grafana, Loki, Blackbox, Node Exporter
├── docs/
│   ├── architecture.md
│   └── decisions.md
└── Makefile
```

## Quick Start

```bash
# 1. Install k3s
curl -sfL https://get.k3s.io | sh -
mkdir -p ~/.kube && sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

# 2. Install Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 3. Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# 4. Deploy everything
make install DOMAIN=todo.example.com DB_PASSWORD=secret GRAFANA_PASSWORD=secret

# 5. Check status
make status
```

## Makefile Commands

| Command | Description |
|---|---|
| `make install` | Deploy all Helm charts to cluster |
| `make upgrade` | Upgrade backend and frontend charts |
| `make lint` | Lint all Helm charts |
| `make template` | Render templates without deploying |
| `make status` | Show pods, services, ingresses |
| `make uninstall` | Remove all releases |
| `make clean` | Uninstall + delete namespace |

## Helm Hooks

The `backend` chart includes a **post-install Job** that:
1. Waits for the backend to be ready (initContainer with curl retry loop)
2. Seeds initial tasks via REST API

## Database Backup

A daily CronJob (00:00 UTC) runs `mysqldump` and stores the dump in a PVC:

```bash
kubectl get cronjob -n todo-app
kubectl get pvc -n todo-app
```

## Security

- Secrets passed via `--set` flags, never committed to `values.yaml`
- Each chart has `values.example.yaml` showing required fields
- Backend runs as non-root (UID 1000, `runAsNonRoot: true`)
- MySQL accessible only within cluster (ClusterIP)

## 🔗 Part of the DevOps Portfolio Series

| # | Repository | Description |
|---|---|---|
| 1 | [aws-terraform-infra](https://github.com/samarets-vlad/aws-terraform-infra) | Cloud foundation — VPC, ALB, EC2, RDS, S3 |
| 2 | [ansible-server-setup](https://github.com/samarets-vlad/ansible-server-setup) | Server configuration — Nginx, Docker, TLS |
| 3 | [docker-ecr-ec2-pipeline](https://github.com/samarets-vlad/docker-ecr-ec2-pipeline) | CI/CD — Docker build → ECR → EC2 |
| 4 | [monitoring-stack](https://github.com/samarets-vlad/monitoring-stack) | Observability — Prometheus, Grafana, Alertmanager |
| 5 | 👉 **k8s-helm-app** | Kubernetes — k3s, Helm, Traefik, cert-manager |
| 6 | [serverless-aws-pipeline](https://github.com/samarets-vlad/serverless-aws-pipeline) | Serverless — Lambda, API GW, S3, CloudFront |
