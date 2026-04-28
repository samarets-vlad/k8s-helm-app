.PHONY: install upgrade uninstall lint template status clean

NAMESPACE ?= todo-app
DOMAIN ?= todo.example.com
DB_PASSWORD ?= changeme
GRAFANA_PASSWORD ?= changeme

install:
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	helm install database helm-charts/database -n $(NAMESPACE) --set auth.rootPassword=$(DB_PASSWORD) --set auth.password=$(DB_PASSWORD)
	helm install backend helm-charts/backend -n $(NAMESPACE) --set mysql.password=$(DB_PASSWORD)
	helm install frontend helm-charts/frontend -n $(NAMESPACE)
	helm install ingress helm-charts/ingress -n $(NAMESPACE) --set host=$(DOMAIN)
	helm install backup helm-charts/backup -n $(NAMESPACE)
	helm install monitoring helm-charts/monitoring -n $(NAMESPACE) --set grafana.adminPassword=$(GRAFANA_PASSWORD)

upgrade:
	helm upgrade backend helm-charts/backend -n $(NAMESPACE)
	helm upgrade frontend helm-charts/frontend -n $(NAMESPACE)

status:
	kubectl get pods,svc,ingress -n $(NAMESPACE)

lint:
	helm lint helm-charts/backend helm-charts/frontend helm-charts/database helm-charts/ingress helm-charts/backup helm-charts/monitoring

template:
	helm template backend helm-charts/backend --set mysql.password=test

uninstall:
	helm uninstall database backend frontend ingress backup monitoring -n $(NAMESPACE) || true

clean: uninstall
	kubectl delete namespace $(NAMESPACE) || true
