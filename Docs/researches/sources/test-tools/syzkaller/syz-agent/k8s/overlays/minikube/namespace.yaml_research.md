# sources/test-tools/syzkaller/syz-agent/k8s/overlays/minikube/namespace.yaml

Purpose: declares the local `syz-agent` namespace.

Important APIs/types/functions: Kubernetes `Namespace`.

Control flow: applied as part of minikube overlay.

State and persistence: cluster namespace object.

Dependencies and integration points: required by namespaced syz-agent resources.

Risks: none beyond namespace collision.

Test signals: namespace creation/admission.
