# sources/test-tools/syzkaller/syz-cluster/email-reporter/lore-disk-pvc.yaml

## Purpose
Defines persistent storage for the email reporter's Lore repository checkout.

## Important APIs, types, and functions
Creates a `v1` `PersistentVolumeClaim` named `reporter-lore-disk-claim` with `ReadWriteOnce`, 16Gi request, and `standard` storage class.

## Control flow
The email reporter deployment mounts this claim at `/lore-repo`; `MakeLorePoller` uses `/lore-repo/checkout` as its repository directory.

## State and persistence behavior
Persists the cloned/fetched Lore archive state across pod restarts, reducing fetch cost and preserving poller continuity.

## Dependencies and integration points
Requires a cluster storage class named `standard`. Mounted by `deployment.yaml`.

## Risks and edge cases
`ReadWriteOnce` aligns with the single-replica design; scaling replicas would not work safely with this claim. A too-small disk could break long-running Lore archive growth.

## Test signals
No direct test; deployment smoke or production monitoring would surface storage provisioning/mount failures.
