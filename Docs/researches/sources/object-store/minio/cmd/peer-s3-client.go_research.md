# sources/object-store/minio/cmd/peer-s3-client.go

## Purpose
This file implements clustered S3 bucket operations across MinIO peers with pool-aware quorum semantics.

## Important APIs, Types, and Functions
`peerS3Client` abstracts bucket list/heal/head/make/delete plus host and pool metadata. `localPeerS3Client` calls local helpers directly. `remotePeerS3Client` calls grid RPCs. `S3PeerSys` owns peer clients and pool count. `HealBucket`, `ListBuckets`, `GetBucketInfo`, `MakeBucket`, and `DeleteBucket` fan out to peers using `errgroup.WithNErrs` and reduce errors per pool.

## Control Flow and State
Peer clients are built from endpoint nodes, including the local node. Remote grid connections are lazily cached via atomic pointers. Each cluster operation gathers per-node responses, groups errors by pool membership, applies read/write quorum reducers, and returns object-layer errors. `ListBuckets` also queues partial bucket heals when bucket quorum is lost.

## Dependencies and Integration Points
The file depends on `peer-s3-server.go` local helpers, grid handlers declared in `peer-rest-server.go`, endpoint pool metadata, `globalDriveConfig`, `globalMRFState`, and MinIO quorum reducers.

## Risks and Test Signals
Nil grid connections currently return nil results for some remote calls, which can be treated as success and may weaken immediate consistency during startup. Delete rollback recreates buckets unless `NoRecreate` is set. Pool quorum logic is central to correctness and should be covered by distributed bucket operation tests, though no direct tests are in this subset.
