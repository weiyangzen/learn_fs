# sources/test-tools/syzkaller/syz-agent/k8s/common/kustomization.yaml

Purpose: base Kustomize bundle for syz-agent.

Important APIs/types/functions: `Kustomization` with resources `syz-agent.yaml` and `network-policy.yaml`.

Control flow: Kustomize includes the StatefulSet and NetworkPolicy for overlays.

State and persistence: no runtime state itself; references resources that create PVCs and network policy.

Dependencies and integration points: consumed by minikube and prod-agent overlays.

Risks: base namespace expectations rely on overlays or manifest namespace fields.

Test signals: `kubectl kustomize` rendering.
