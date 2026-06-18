# sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/kustomization.yaml

## Purpose
Production GKE Kustomize overlay.

## Important APIs, types, and functions
Includes `../common` and creates a config map generator named `global-config` from `global-config.yaml`.

## Control flow
Rendering composes GKE common resources with production config data.

## State and persistence behavior
No state; config map content drives production runtime behavior.

## Dependencies and integration points
Depends on GKE common overlay and all base resources. Components mount/read the generated `global-config`.

## Risks and edge cases
ConfigMap generator name hashing behavior must align with deployment references or be disabled elsewhere. Production and staging differ primarily through their global config.

## Test signals
Kustomize build/deployment validation; no direct tests in file.
