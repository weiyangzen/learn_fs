# sources/test-tools/syzkaller/syz-cluster/overlays/common/kustomization.yaml

## Purpose
Composes the shared syz-cluster base resources and common network policies.

## Important APIs, types, and functions
Includes controller, dashboard, series-tracker, kernel-disk, reporter-server, workflow, and multiple network policy resources. Applies a JSON patch to all `Deployment` resources replacing the first container's `imagePullPolicy` with `IfNotPresent`.

## Control flow
Environment-specific overlays include this common overlay, then add infra/config/storage/service-account resources.

## State and persistence behavior
No state itself, but it brings in components that use Spanner, blob storage, PVCs, and workflows.

## Dependencies and integration points
Central integration point for most syz-cluster workloads. Network policies here assume consistent pod labels across component deployments and workflow pods.

## Risks and edge cases
The imagePullPolicy patch targets `/containers/0`; multi-container deployments or reordered containers could be patched incorrectly. Omitting email-reporter from common resources means it must be included elsewhere when needed. Label drift can invalidate network policies.

## Test signals
Core manifest path for `local_cluster_test.sh` and Kustomize targets.
