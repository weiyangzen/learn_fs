# sources/test-tools/syzkaller/syz-agent/Makefile

Purpose: build and render deployment artifacts for syz-agent and lore-relay.

Important APIs/types/functions: targets `agent-container`, `lore-relay-container`, `all-containers`, `k8s-minikube`, `k8s-prod-agent`, and `k8s-prod-lore`.

Control flow: container targets run Docker builds with revision/image variables. Kubernetes targets run `kubectl kustomize` overlays and substitute image tags and secrets/env placeholders with `sed`.

State and persistence: writes Docker images to local/remote image stores when builds run; emits YAML to stdout for k8s targets.

Dependencies and integration points: includes `../tools/version.mk`; consumes the Dockerfiles and kustomize overlays in this subtree.

Risks: sed substitution of secret values is shell-sensitive; minikube target explicitly requires env vars. Rendered manifests still contain externally managed service accounts in prod.

Test signals: `make k8s-*` rendering and Docker build success.
