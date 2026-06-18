# sources/test-tools/syzkaller/syz-cluster/kernel-disk/kustomization.yaml

## Purpose
Kustomize base for kernel repository fetch workflows.

## Important APIs, types, and functions
Includes `fetch-kernels-template.yaml` and `fetch-kernels-cron.yaml`. The one-shot workflow is intentionally not included by default.

## Control flow
Overlays including kernel-disk get the reusable template and scheduled cron.

## State and persistence behavior
State is provided by environment overlays that define `base-kernel-repo-pv-claim`.

## Dependencies and integration points
Pulled into `overlays/common/kustomization.yaml` and then local/GKE overlays.

## Risks and edge cases
A missing PVC or Argo installation makes rendered resources fail at runtime even if Kustomize succeeds.

## Test signals
Indirectly included in local cluster smoke deployment.
