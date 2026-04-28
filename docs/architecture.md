# Architecture

## Cluster Overview

```
          Internet
              │
     ┌───────┴───────┐
     │   Traefik     │  :80 / :443 (Ingress)
     │ (cert-manager)│
     └───────┬───────┘
              │
     ┌───────┴───────┐
     │   Frontend   │  nginx + HTML (ClusterIP)
     └───────┬───────┘
              │ REST /api
     ┌───────┴───────┐
     │   Backend    │  Python Flask :5000 (ClusterIP, 2 replicas)
     └───────┬───────┘
              │
     ┌───────┴───────┐
     │   MySQL 8.0  │  :3306 (ClusterIP, PVC)
     └───────────────┘

Monitoring namespace:
  Prometheus → scrapes all pods
  Grafana    → dashboards
  Loki       → log aggregation (Promtail)
  Blackbox   → endpoint probing
  Node Exporter → host metrics

Backup CronJob: daily 00:00 UTC → mysqldump → PVC
```

## Helm Charts

| Chart | Resources |
|---|---|
| `backend` | Deployment (2 replicas), Service, Secret, post-install Hook |
| `frontend` | Deployment, Service |
| `database` | StatefulSet, Service, PVC, Secret |
| `ingress` | IngressRoute (Traefik), Certificate (cert-manager) |
| `backup` | CronJob, PVC |
| `monitoring` | Prometheus, Grafana, Loki, Promtail, Blackbox, Node Exporter |

## Helm Hook Flow

```
helm install backend
    │
    ├── Deploy Deployment + Service + Secret
    └── post-install Job:
           initContainer: wait-for-backend (curl retry loop)
           container: seed initial tasks via REST API
```
