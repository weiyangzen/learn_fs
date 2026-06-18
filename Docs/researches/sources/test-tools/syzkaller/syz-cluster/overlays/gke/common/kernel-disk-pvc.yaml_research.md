# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kernel-disk-pvc.yaml

## Purpose
Defines GKE Filestore-backed shared storage for base kernel repositories.

## Important APIs, types, and functions
Creates `StorageClass` `filestore-custom` using provisioner `filestore.csi.storage.gke.io`, tier `standard`, network `gke-network`, immediate binding, and expansion support. Creates PVC `base-kernel-repo-pv-claim` with `ReadWriteMany` and 1Ti request.

## Control flow
Kernel fetch workflows mount this claim and update a shared bare git repository.

## State and persistence behavior
Persists kernel git repositories across workflow runs and supports multi-reader/multi-writer access through Filestore.

## Dependencies and integration points
Depends on GKE Filestore CSI driver, network `gke-network`, and workflow templates referencing the claim name.

## Risks and edge cases
1Ti is noted as the minimum, so cost and capacity are significant. Shared write behavior still needs workflow concurrency controls to avoid git conflicts.

## Test signals
Runtime storage provisioning and workflow execution validate this. Local smoke uses a different PVC.
