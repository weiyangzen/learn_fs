# sources/test-tools/syzkaller/syz-agent/k8s/overlays/minikube/kustomization.yaml

Purpose: local Kustomize overlay for running one syz-agent replica on minikube.

Important APIs/types/functions: sets namespace `syz-agent`, namePrefix `local-`, includes common resources plus namespace/serviceaccount, overrides image, generates config map, and patches the StatefulSet.

Control flow: patch reduces replicas to one, injects `GOOGLE_API_KEY` and `DASHBOARD_KEY`, and sets `imagePullPolicy: IfNotPresent`.

State and persistence: inherits StatefulSet PVC behavior.

Dependencies and integration points: rendered by `make k8s-minikube` with sed substitutions.

Risks: secrets are substituted into rendered YAML as plain values. Name prefix affects resource names but patches target the pre-prefix logical name.

Test signals: kustomize render and minikube rollout.
