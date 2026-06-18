# sources/test-tools/syzkaller/syz-agent/k8s/overlays/prod-agent/kustomization.yaml

Purpose: production syz-agent Kustomize overlay.

Important APIs/types/functions: namespace/namePrefix, common resources, image override, configMapGenerator, and StatefulSet patch.

Control flow: generates config map from prod config, patches node selector for nested virtualization, adds toleration for nested-vm workload, and injects `GIT_COOKIE_DAEMON`.

State and persistence: inherits StatefulSet PVCs and config map.

Dependencies and integration points: Terraform-provided namespace/service account are assumed; rendered by `make k8s-prod-agent`.

Risks: scheduling depends on custom node label and toleration. `GIT_COOKIE_DAEMON` is substituted through sed and controls background credential helper startup.

Test signals: kustomize render, scheduling on nested virtualization nodes, and agent startup.
