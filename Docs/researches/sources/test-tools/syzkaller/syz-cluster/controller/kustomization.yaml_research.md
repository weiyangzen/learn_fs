# sources/test-tools/syzkaller/syz-cluster/controller/kustomization.yaml

Purpose: Kustomize component bundle for controller.

Important APIs/types/functions: resource list including `deployment.yaml` and `service.yaml`.

Control flow: parent overlays include this bundle to deploy controller workload and service.

State and persistence: none directly.

Dependencies and integration points: used by syz-cluster kustomize overlays.

Risks: no apiVersion/kind in this older-style kustomization; accepted by kustomize but less explicit.

Test signals: kustomize render.
