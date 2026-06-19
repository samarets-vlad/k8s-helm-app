# k8s Helm App — Todo App на k3s

> 🇬🇧 [English version](README.md)

Full-stack **Todo застосунок**, розгорнутий на одновузловому **k3s** кластері за допомогою **Helm charts**.
Демонструє продакшен-підхід до DevOps: параметризовані Helm-чарти, TLS через cert-manager,
стек спостережуваності (Prometheus + Grafana + Loki), автоматичні бекапи та Helm hooks.

## Стек

| Рівень | Технологія |
|---|---|
| Kubernetes | k3s v1.34+ |
| Ingress | Traefik (вбудований у k3s) |
| TLS | cert-manager + Let's Encrypt |
| Package Manager | Helm v3 |
| Backend | Python Flask — `vladdisslav/todo-backend:v1.0.0` |
| Frontend | Nginx + HTML |
| База даних | MySQL 8.0 |
| Моніторинг | Prometheus, Grafana, Loki, Promtail, Blackbox, Node Exporter |
| Бекап | Kubernetes CronJob → PVC (щоденний mysqldump) |

## Архітектура

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

## Структура репозиторію

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
│   ├── backup/             ← CronJob (щоденний mysqldump → PVC)
│   └── monitoring/         ← Prometheus, Grafana, Loki, Blackbox, Node Exporter
├── docs/
│   ├── architecture.md
│   └── decisions.md
└── Makefile
```

## Швидкий старт

```bash
# 1. Встановити k3s
curl -sfL https://get.k3s.io | sh -
mkdir -p ~/.kube && sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config

# 2. Встановити Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# 3. Встановити cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# 4. Розгорнути весь стек
make install DOMAIN=todo.example.com DB_PASSWORD=secret GRAFANA_PASSWORD=secret

# 5. Перевірити статус
make status
```

## Команди Makefile

| Команда | Опис |
|---|---|
| `make install` | Розгорнути всі Helm-чарти в кластері |
| `make upgrade` | Оновити backend та frontend чарти |
| `make lint` | Запустити `helm lint` для всіх чартів |
| `make template` | Зрендерити шаблони без деплою |
| `make status` | Показати pods, services, ingresses |
| `make uninstall` | Видалити всі релізи |
| `make clean` | Uninstall + видалення namespace |

## Helm Hooks

Чарт `backend` містить **post-install Job**, який:
1. Чекає готовності backend (initContainer з циклом перевірки через curl)
2. Створює початкові задачі через REST API

## Бекап бази даних

Щоденний CronJob (00:00 UTC) запускає `mysqldump` і зберігає дамп у PVC:

```bash
kubectl get cronjob -n todo-app
kubectl get pvc -n todo-app
```

## Безпека

- Секрети передаються через `--set` / змінні оточення, не комітяться у `values.yaml`
- Кожен чарт має `values.example.yaml` із прикладами обов'язкових полів
- Backend працює від non-root користувача (UID 1000, `runAsNonRoot: true`)
- MySQL доступна лише всередині кластера (ClusterIP)

## 🔗 Частина DevOps Portfolio Series

| # | Репозиторій | Опис |
|---|-------------|------|
| 1 | [aws-terraform-infra](https://github.com/samarets-vlad/aws-terraform-infra) | Cloud foundation — VPC, ALB, EC2, RDS, S3 |
| 2 | [ansible-server-setup](https://github.com/samarets-vlad/ansible-server-setup) | Налаштування серверів — Nginx, Docker, TLS |
| 3 | [docker-ecr-ec2-pipeline](https://github.com/samarets-vlad/docker-ecr-ec2-pipeline) | CI/CD — Docker build → ECR → EC2 |
| 4 | [monitoring-stack](https://github.com/samarets-vlad/monitoring-stack) | Observability — Prometheus, Grafana, Alertmanager |
| 5 | 👉 **k8s-helm-app** | Kubernetes — k3s, Helm, Traefik, cert-manager |
| 6 | [serverless-aws-pipeline](https://github.com/samarets-vlad/serverless-aws-pipeline) | Serverless — Lambda, API GW, S3, CloudFront |
