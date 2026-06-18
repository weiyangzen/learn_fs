# sources/test-tools/syzkaller/syz-agent/k8s/overlays/prod-lore/kustomization.yaml

Purpose: production lore-relay Kustomize overlay.

Important APIs/types/functions: namespace `lore-relay`, namePrefix `prod-`, common lore-relay resources, image override, and configMapGenerator.

Control flow: includes base deployment/PVC and generates the relay config map from `lore-relay-config.yaml`.

State and persistence: inherits lore relay PVC for checkout state.

Dependencies and integration points: rendered by `make k8s-prod-lore`.

Risks: no namespace/service account resource here; expected to be provisioned externally.

Test signals: kustomize render and prod rollout.
