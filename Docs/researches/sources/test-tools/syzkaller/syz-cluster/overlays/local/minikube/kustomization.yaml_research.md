# sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/kustomization.yaml

## Purpose
Minikube/local development Kustomize overlay.

## Important APIs, types, and functions
Includes `../common` and `../../common`, and generates `global-config` from `global-config.yaml`.

## Control flow
Builds local infrastructure plus common application resources with minikube/debug config.

## State and persistence behavior
Uses local emulator/PVC state from local common.

## Dependencies and integration points
Depends on local common infrastructure and shared app common overlay.

## Risks and edge cases
Layer ordering matters because it includes both infrastructure and app resources. ConfigMap generator naming must align with consumers.

## Test signals
Manual minikube deployment path; not the main smoke test overlay.
