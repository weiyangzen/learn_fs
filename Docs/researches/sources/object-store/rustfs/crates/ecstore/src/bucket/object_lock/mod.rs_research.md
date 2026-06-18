# sources/object-store/rustfs/crates/ecstore/src/bucket/object_lock/mod.rs

Purpose: Defines the object lock module boundary and small extension traits over S3 DTO types.

Important APIs and types: Exports `objectlock` and `objectlock_sys`. `ObjectLockApi::enabled` is implemented for `ObjectLockConfiguration` and returns true when `ObjectLockEnabled` equals `ENABLED`. `ObjectLockStatusExt::valid` is implemented for `ObjectLockLegalHoldStatus` and accepts only `ON` and `OFF`.

Control flow and state: Stateless trait adapters centralize DTO string comparisons so metadata and enforcement code do not repeat them. `BucketMetadata::versioning` uses `ObjectLockApi::enabled` to treat object lock as versioning-enabling state.

Dependencies and integration: Depends on S3 DTO object-lock types. Consumed by `metadata.rs` and object-lock enforcement paths.

Risks: String comparison depends on the DTO constants' exact casing and representation. The file validates legal hold status values but does not validate retention modes or dates; those live in `objectlock.rs` and `objectlock_sys.rs`.

Test signals: No direct tests. Behavior is indirectly covered by object-lock parser/system tests and metadata versioning behavior.
