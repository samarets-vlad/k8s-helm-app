# Architecture Decision Records

## ADR-001: k3s over full Kubernetes

**Decision**: Use k3s on a single VPS instead of a managed cluster (EKS/GKE).

**Reason**: Single-node VPS is cost-effective for a demo. k3s includes Traefik ingress and uses less RAM (~512MB vs ~2GB for full k8s).

## ADR-002: Helm over raw manifests

**Decision**: Package each component as a Helm chart with `values.yaml`.

**Reason**: Parameterised deployments, reusable templates, easy upgrades via `helm upgrade`. Demonstrates real-world packaging skills.

## ADR-003: Secrets via --set, not values.yaml

**Decision**: Pass passwords via `--set` flags or CI secrets, never commit them to `values.yaml`.

**Reason**: Prevents accidental secret leakage. Each chart has a `values.example.yaml` showing required fields without real values.

## ADR-004: post-install Hook for seeding

**Decision**: Use a Helm post-install Job with an initContainer retry loop instead of a simple Job.

**Reason**: The backend needs the database to be fully ready before seeding. The initContainer polls `/api` until it responds, ensuring correct ordering without manual intervention.

## ADR-005: Separate monitoring chart

**Decision**: Bundle Prometheus, Grafana, Loki, and Blackbox into one `monitoring` chart.

**Reason**: Simplifies installation to a single `helm install`. All monitoring components are versioned together and can be toggled via values.
