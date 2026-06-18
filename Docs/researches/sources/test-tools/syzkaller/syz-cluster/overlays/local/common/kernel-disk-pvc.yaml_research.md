# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kernel-disk-pvc.yaml

## Purpose
Defines local shared storage for kernel repository cache.

## Important APIs, types, and functions
Creates PVC `base-kernel-repo-pv-claim` using storage class `standard`, access mode `ReadWriteMany`, and 32Gi request.

## Control flow
Kernel fetch workflows mount this claim at `/repo.git`.

## State and persistence behavior
Persists bare git repository data within the local cluster storage backend.

## Dependencies and integration points
Requires a local storage class that supports `ReadWriteMany`; this can be cluster-specific.

## Risks and edge cases
Many local Kubernetes defaults do not support RWX on `standard`. If unsupported, workflows remain pending. 32Gi may be too small for broad kernel mirror use.

## Test signals
Smoke deployment may catch PVC provisioning failures depending on whether workflow resources are scheduled during the test.
