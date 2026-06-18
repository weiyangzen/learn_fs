# sources/object-store/minio/cmd/object-api-interface.go

## Purpose
This file defines the central `ObjectLayer` interface and option structs used by MinIO object API implementations. It is the contract between S3/API handlers and backend object storage implementations for bucket, object, multipart, healing, metadata, tagging, health, and lifecycle/transition operations.

## Important APIs, types, and functions
`ObjectOptions` is the main cross-operation carrier. It includes server-side encryption, versioning state, version ID, modification/expiration time, delete marker and delete replication state, tagging and object attribute request data, precondition and metadata callbacks, transition/expiration options, checksum requests, decryption flags, ETag preservation, proxy/replication flags, source timestamps for replicated metadata, prefix deletion flags, speedtest flags, parity/encryption callbacks, decommission/rebalance routing flags, data movement flags, versioning prefix callback, index callback, free-version controls, retention bypass callback, fast head/get flag, and audit suppression.

`WalkOptions`, `ExpirationOptions`, `TransitionOptions`, `MakeBucketOptions`, `DeleteBucketOptions`, and `BucketOptions` define narrower option sets. Helper methods on `ObjectOptions` maintain replication state: `SetReplicaStatus`, `DeleteMarkerReplicationStatus`, `VersionPurgeStatus`, `SetDeleteReplicationState`, `PutReplicationState`, `SetEvalMetadataFn`, and `SetEvalRetentionBypassFn`.

`ObjectLayer` includes namespace locking, scanner/backend/storage info, bucket CRUD and listing, object get/info/put/copy/delete/transition/restore, multipart lifecycle, disk access, healing, health, metadata update, tiered decommission, and object tag operations. `GetObject` is a compatibility adapter around `GetObjectNInfo` that copies the returned reader to an `io.Writer`.

## Control flow
The interface itself has no implementation flow, but it defines expected operation sequencing. `GetObject` builds an HTTP range spec and optional ETag header, calls `GetObjectNInfo`, returns immediately on error, closes the reader with `defer`, and copies data via `xioutil.Copy`. The interface comment requires implementations to return a nil reader when returning an error from `GetObjectNInfo`.

## State and persistence behavior
State is represented as options and backend mutations rather than stored in this file. The interface covers persistent bucket/object namespace changes, multipart metadata, object versioning/delete-marker state, replication metadata, healing state, object tags, and tier transition state. Option fields such as `NoLock`, `SkipDecommissioned`, `SkipRebalancing`, `SrcPoolIdx`, and `DataMovement` affect how implementations coordinate persistent writes across pools and disks.

## Dependencies and integration points
The file imports `madmin-go`, MinIO encryption and tag packages, internal hash/checksum and replication packages, HTTP types, and internal I/O helpers. It is a high fan-in integration point for S3 handlers, replication, lifecycle, scanner/healing, metadata systems, object-lock enforcement, and tests. The `go:generate msgp` directive and `msgp:ignore` annotations connect this source to the generated serialization companion.

## Risks and test signals
`ObjectOptions` is broad and easy to misuse; many fields are valid only for specific operations. Regressions can arise when handlers forget to set versioning or replication flags, when backend implementations ignore callback fields, or when generated serialization falls out of sync for serializable option types. The tests in this subset exercise portions of the interface through delete, get info, list, multipart, option parsing, and object attributes, but many interface methods require coverage elsewhere.
