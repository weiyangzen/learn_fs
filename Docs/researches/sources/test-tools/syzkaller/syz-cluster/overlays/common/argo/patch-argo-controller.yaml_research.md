# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-argo-controller.yaml

## Purpose
Patches the Argo workflow-controller deployment to use the expected controller service account.

## Important APIs, types, and functions
Targets `apps/v1` `Deployment` `workflow-controller` in namespace `argo` and sets `spec.template.spec.serviceAccountName` to `argo-controller-ksa`. Includes kube-linter annotation for Terraform-defined account handling.

## Control flow
Kustomize applies this patch on top of Argo's upstream install manifest.

## State and persistence behavior
No data persistence. It changes runtime identity and therefore permissions.

## Dependencies and integration points
Depends on `workflow-roles.yaml` defining role bindings for `argo-controller-ksa` and on service account creation in the selected environment.

## Risks and edge cases
If the service account does not exist, the controller pod fails admission/startup. If upstream Argo deployment name/namespace changes, the patch misses its target.

## Test signals
Smoke deployment would fail if Argo controller cannot start because of service account mismatch.
