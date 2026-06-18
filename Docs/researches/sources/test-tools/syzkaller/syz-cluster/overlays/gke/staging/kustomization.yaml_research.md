# sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/kustomization.yaml

## Purpose
Staging GKE Kustomize overlay.

## Important APIs, types, and functions
Includes `../common` and generates `global-config` from staging `global-config.yaml`.

## Control flow
Builds the GKE common stack with staging runtime config.

## State and persistence behavior
No state; generated config map drives staging behavior.

## Dependencies and integration points
Same as prod overlay but with staging-specific config.

## Risks and edge cases
Same configMapGenerator name/reference considerations as production. Staging-only config drift can hide production issues.

## Test signals
Kustomize/deployment validation only.
