# sources/sync-backup/git-lfs/t/t-batch-transfer-size.sh

## Purpose
Tests `lfs.transfer.batchSize` for upload and download. It ensures multiple objects are split into one-object batch API requests when batch size is configured to `1`.

## Important APIs, Functions, and Control Flow
The upload test commits three LFS objects, sets local `lfs.transfer.batchSize 1`, pushes, and expects three `tq: sending batch of size 1` trace lines. The download test pushes three objects, sets global batch size to `1`, clones, and expects the same trace count during clone.

## State, Persistence, and Dependencies
State includes local/global Git config, remote object store, and trace logs. The tests depend on `setup_remote_repo`, `clone_repo`, `calc_oid`, `assert_server_object`, and `assert_local_object`.

## Integration Points, Risks, and Test Signals
Integration is with transfer queue batching before batch API calls. Signals are exact batch-size trace counts and object presence checks. Risks include global config leakage and trace string changes.
