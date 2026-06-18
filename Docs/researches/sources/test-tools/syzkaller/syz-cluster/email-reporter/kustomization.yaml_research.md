# sources/test-tools/syzkaller/syz-cluster/email-reporter/kustomization.yaml

## Purpose
Kustomize base for the email reporter component.

## Important APIs, types, and functions
Includes `deployment.yaml` and `lore-disk-pvc.yaml` as resources.

## Control flow
Overlays that include this directory render both the workload and persistent volume claim needed for Lore polling.

## State and persistence behavior
Delegates state definition to the PVC and deployment volume mount.

## Dependencies and integration points
Used by environment overlays when email reporting is enabled. It must be paired with global config and network policies that allow reporter/controller/email access.

## Risks and edge cases
If included in a local overlay without a compatible storage class or service accounts, deployment can fail. The base itself does not patch environment-specific service accounts.

## Test signals
Covered only through Kustomize/render/deployment smoke paths, not direct unit tests.
