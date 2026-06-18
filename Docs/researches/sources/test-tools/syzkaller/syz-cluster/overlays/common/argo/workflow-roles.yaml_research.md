# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/workflow-roles.yaml

## Purpose
Defines RBAC needed by Argo workflow executors/controllers and syz-cluster service accounts.

## Important APIs, types, and functions
Creates `ClusterRole` `argo-workflow-role` for workflow CRUD/status, `ClusterRole` `argo-workflowtasks-role` for workflow task result/taskset/artifact GC operations, several `ClusterRoleBinding` and `RoleBinding` resources for executor/controller/service accounts, and a service-account-token `Secret` for `argo-executor-ksa`.

## Control flow
Kubernetes RBAC authorizes workflow creation/updates and task result publication by the specified service accounts.

## State and persistence behavior
No application data. The token secret creates credential material for the executor service account.

## Dependencies and integration points
Assumes service accounts `argo-executor-ksa`, `argo-controller-ksa`, and `gke-service-ksa` in relevant namespaces, plus upstream Argo roles `argo-cluster-role` and `argo-role`. Used by Argo patches and workflow templates.

## Risks and edge cases
Cluster-wide permissions are broad and security-sensitive. Namespace mismatches or missing upstream role names break bindings. Manually creating service-account-token secrets is version-sensitive in newer Kubernetes service account token practices.

## Test signals
Failures surface when Argo controller/executor cannot create, update, or report workflow state. No direct unit tests.
