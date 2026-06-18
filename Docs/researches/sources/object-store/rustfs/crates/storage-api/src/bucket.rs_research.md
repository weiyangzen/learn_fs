# sources/object-store/rustfs/crates/storage-api/src/bucket.rs

## Purpose
Defines bucket option and metadata DTOs shared by storage APIs.

## Important APIs and Types
`MakeBucketOptions` includes object-lock, versioning, force-create, optional creation time, and no-lock flags. `SRBucketDeleteOp` models site-replication delete behavior as `NoOp`, `MarkDelete`, or `Purge`. `DeleteBucketOptions` includes locking/recreate/force flags plus site-replication delete op. `BucketOptions` controls list/get behavior for deleted/cached/no-metadata variants. `BucketInfo` serializes bucket name, created/deleted timestamps, versioning, and object locking.

## Control Flow, State, and Persistence
These are passive DTOs. Persistence is via serde for `MakeBucketOptions`, `BucketOptions`, and `BucketInfo`; `DeleteBucketOptions` and `SRBucketDeleteOp` are currently not serde-enabled in this file.

## Integration Points
Re-exported by `storage-api/src/lib.rs` and used by scanner lifecycle tests through `MakeBucketOptions`. Storage crates use these values for bucket create/delete/list contracts.

## Risks
Most structs derive `Default`, so new boolean fields default to false; this must match storage semantics. `SRBucketDeleteOp` lacks `Eq`, `Serialize`, and `Deserialize`, which may limit wire/config use. Time serialization depends on workspace `time` serde configuration.

## Test Signals
Tests verify `BucketInfo` JSON round trip, default `BucketOptions` false flags, and default `DeleteBucketOptions` using `SRBucketDeleteOp::NoOp` with false flags.
