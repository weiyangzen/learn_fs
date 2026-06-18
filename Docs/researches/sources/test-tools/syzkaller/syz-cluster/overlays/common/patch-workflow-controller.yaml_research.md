# sources/test-tools/syzkaller/syz-cluster/overlays/common/patch-workflow-controller.yaml

## Purpose
Patches Argo workflow-controller service account in the common overlay outside the `argo/` suboverlay.

## Important APIs, types, and functions
Targets `apps/v1` `Deployment` `workflow-controller` in namespace `argo` and sets `serviceAccountName` to `argo-workflows-ksa`.

## Control flow
If included as a Kustomize patch, it changes the controller identity used by the Argo controller pod.

## State and persistence behavior
No application state; affects RBAC identity.

## Dependencies and integration points
Potentially overlaps with `overlays/common/argo/patch-argo-controller.yaml`, which sets `argo-controller-ksa`. The researched `overlays/common/kustomization.yaml` does not include this file directly.

## Risks and edge cases
Conflicting service account names across patch files can cause environment drift if both are ever applied. Because it appears unused by the researched common kustomization, it may be legacy or intended for another path.

## Test signals
No direct signal unless an overlay includes it. Argo controller startup would reveal service-account mismatch.
