# sources/test-tools/syzkaller/syz-cluster/dashboard/service.yaml

## Purpose
Exposes the dashboard deployment inside the Kubernetes cluster.

## Important APIs, types, and functions
Defines a `v1` `Service` named `web-dashboard-service` selecting pods labeled `app: web-dashboard`. It exposes service port `80` to target port `8081`.

## Control flow
Traffic to the service on port 80 is forwarded by Kubernetes to dashboard pods on port 8081, matching `main.go`.

## State and persistence behavior
No persistence. The service tracks matching endpoints dynamically through pod labels.

## Dependencies and integration points
Consumed by common and GKE overlays. The GKE common overlay patches metadata annotations for a Google Cloud NEG on exposed port 80. `local_cluster_test.sh` port-forwards this service and expects HTTP 200 from `/`.

## Risks and edge cases
Selector/label drift between deployment and service would break routing. Network policies must allow ingress to the selected pods on the effective target port.

## Test signals
The smoke test validates service reachability through `kubectl port-forward svc/web-dashboard-service 8080:80` and a curl check.
