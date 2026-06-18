# sources/test-tools/syzkaller/syz-agent/k8s/common/lore-relay/kustomization.yaml

Purpose: base Kustomize bundle for lore-relay.

Important APIs/types/functions: `Kustomization` listing `lore-relay.yaml` and `lore-relay-pvc.yaml`.

Control flow: overlays include deployment plus persistent volume claim.

State and persistence: delegates persistence to the PVC resource.

Dependencies and integration points: consumed by `prod-lore` overlay.

Risks: requires external namespace/service account setup in prod.

Test signals: kustomize render success.
