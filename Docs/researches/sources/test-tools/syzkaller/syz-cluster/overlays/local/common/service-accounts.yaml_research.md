# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/service-accounts.yaml

## Purpose
Defines local service accounts and RBAC bindings that GKE/Terraform would otherwise provide.

## Important APIs, types, and functions
Creates service accounts including `gke-service-ksa`, `argo-executor-ksa`, `argo-controller-ksa`, and `kernel-fetcher-ksa` in namespace `default` or `argo` as appropriate. Adds a `ClusterRoleBinding` for `kernel-fetcher-ksa` to `argo-workflowtasks-role`.

## Control flow
Local overlays create these identities before workloads and workflows refer to them.

## State and persistence behavior
No application data; establishes Kubernetes identities.

## Dependencies and integration points
Integrates with Argo RBAC in `workflow-roles.yaml`, workflow templates, local deployments, and GKE-compatible service account names.

## Risks and edge cases
The service account set must stay in sync with deployment manifests and Argo patches. Binding kernel fetcher to workflow task role is necessary for Argo executor reporting, but any missing broader permissions could break specialized workflows.

## Test signals
Local cluster smoke catches missing service accounts during pod creation.
