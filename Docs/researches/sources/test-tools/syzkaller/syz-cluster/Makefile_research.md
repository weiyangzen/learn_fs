# sources/test-tools/syzkaller/syz-cluster/Makefile

Purpose: build, containerize, render, and operate syz-cluster components.

Important APIs/types/functions: image list, `build_image_rules` macro, per-component build/push targets, common builder target, kustomize config targets, migration/email/fetch helper targets, and env guards.

Control flow: Go binaries are built into `bin/`, Docker images are built from component Dockerfiles using a common builder image, manifests are rendered through kustomize and sed substitution, and operational targets apply local infra, wait for CRDs/spanner, run migrations, and render job YAML.

State and persistence: creates local binaries and Docker images; may apply Kubernetes resources and run migrations when invoked.

Dependencies and integration points: includes `../tools/version.mk`, uses Docker BuildKit, kubectl/kustomize, minikube, and syz-cluster overlay trees.

Risks: Make macro indentation and sed escaping are critical. Some targets directly mutate Kubernetes clusters. Required env vars are enforced for GKE config targets.

Test signals: `make all`, image builds, kustomize render, and cluster apply/migration success.
