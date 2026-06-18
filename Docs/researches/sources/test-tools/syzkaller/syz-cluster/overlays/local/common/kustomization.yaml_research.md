# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kustomization.yaml

## Purpose
Composes local infrastructure shared by local/minikube/test overlays.

## Important APIs, types, and functions
Includes service accounts, kernel disk PVC, common Argo overlay, local config env, fake GCS, Spanner emulator, Spanner network policy, and workflow artifact config. Applies `patch-workflow-controller-configmap.yaml`.

## Control flow
Local environment overlays include this layer before adding component bases and environment-specific global config.

## State and persistence behavior
Provides emulator-backed state and local PVC state rather than cloud Spanner/GCS/Filestore.

## Dependencies and integration points
Central integration point for local cluster tests and development. Depends on local service accounts/RBAC and fake infrastructure resources.

## Risks and edge cases
Including Argo remote install can require network at build time. Local storage and LoadBalancer behavior vary across kind/minikube.

## Test signals
Directly exercised by `local_cluster_test.sh` through `make k8s-config-local-infra`.
