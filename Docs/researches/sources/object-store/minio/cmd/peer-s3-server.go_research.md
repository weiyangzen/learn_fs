# sources/object-store/minio/cmd/peer-s3-server.go

## Purpose
This file implements local bucket operations used by the peer S3 grid layer: heal, list, stat, delete, and create bucket across local drives.

## Important APIs, Types, and Functions
Constants define peer bucket parameter keys. `healBucketLocal` inspects each local drive, records before/after drive state, optionally deletes dangling buckets, or recreates missing volumes. `listBucketsLocal` lists active and optionally deleted buckets using quorum-aware helpers. `cloneDrives` snapshots the local drive map. `getBucketInfoLocal`, `deleteBucketLocal`, and `makeBucketLocal` run operations across drives with concurrency and quorum reducers.

## Control Flow and State
Each operation snapshots `globalLocalDrivesMap` under read lock, then uses `errgroup.WithNErrs`, often with concurrency 32. Errors are reduced with read or write quorum using `bucketOpIgnoredErrs`. Heal mutates drives only when not dry-run.

## Dependencies and Integration Points
The code integrates with local `StorageAPI` drives, volume APIs, deleted-bucket metadata paths, madmin heal result structures, and peer RPC handlers in `peer-rest-server.go`.

## Risks and Test Signals
Drive snapshots can become stale while operations are running. Heal ignores some delete errors and uses state arrays that must remain aligned with drives. Correctness depends on quorum reducers and storage backends. Peer S3 client tests are not present here, so coverage is likely through distributed object-layer tests.
