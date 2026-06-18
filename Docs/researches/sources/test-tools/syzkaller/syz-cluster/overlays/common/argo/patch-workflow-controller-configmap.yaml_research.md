# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-workflow-controller-configmap.yaml

## Purpose
Sets Argo workflow defaults so workflows run under the expected executor service account.

## Important APIs, types, and functions
Patches `v1` `ConfigMap` `workflow-controller-configmap` in namespace `argo`, setting `data.workflowDefaults` to a YAML snippet with `spec.serviceAccountName: argo-executor-ksa`.

## Control flow
Argo controller reads this config map and applies the default service account to workflows unless overridden.

## State and persistence behavior
No app data; affects workflow execution identity.

## Dependencies and integration points
Integrates with `workflow-roles.yaml`, local service accounts, and workflow templates that may override service accounts for specialized steps.

## Risks and edge cases
Indentation inside the string must remain valid for Argo's config parser. A missing executor service account or RBAC binding breaks workflow pods.

## Test signals
Workflow execution in local smoke or manual runs validates this indirectly.
