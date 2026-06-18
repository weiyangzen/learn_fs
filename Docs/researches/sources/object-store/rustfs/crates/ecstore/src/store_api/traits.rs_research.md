# sources/object-store/rustfs/crates/ecstore/src/store_api/traits.rs

## Purpose

`traits.rs` defines the async interface boundary for ecstore storage implementations. It decomposes the full object-store API into focused traits for object I/O, bucket operations, object metadata and lifecycle operations, listing/walking, multipart upload, healing, and namespace locking. `StorageAPI` then composes the major operation groups into the unified storage contract used by higher-level S3 handlers and service code.

## Important APIs, Types, and Functions

- `ObjectIO` exposes `get_object_reader` and `put_object`. Reads accept bucket/object names, optional `HTTPRangeSpec`, request headers, and `ObjectOptions`, and return `GetObjectReader`. Writes accept `PutObjReader` and return `ObjectInfo`.
- `BucketOperations` contains `make_bucket`, `get_bucket_info`, `list_bucket`, and `delete_bucket`.
- `ObjectOperations` covers `get_object_info`, `verify_object_integrity`, `copy_object`, delete by version, regular delete, batch delete, metadata update, tag get/put/delete, partial markers, transition, and restore of transitioned objects.
- `ListOperations` covers V2 listing, version listing, and a streaming `walk` that sends `ObjectInfoOrErr` through an mpsc channel and accepts a `CancellationToken`.
- `MultipartOperations` includes listing active uploads, creating uploads, copying and uploading parts, fetching multipart metadata, listing parts, aborting uploads, and completing uploads.
- `HealOperations` exposes format, bucket, object, pool/set lookup, and abandoned part checks for repair workflows.
- `NamespaceLocking` exposes `new_ns_lock` for code that needs object mutation coordination without depending on the whole API.
- `StorageAPI` is a marker-like composed trait requiring `ObjectIO + BucketOperations + ObjectOperations + ListOperations + MultipartOperations + HealOperations + Debug`.

## Control Flow

This file has no implementation control flow beyond async trait method declarations. Its control-flow importance is architectural: callers can depend on a narrow trait such as `BucketOperations` or `NamespaceLocking`, while full storage implementations can satisfy `StorageAPI`. Several methods take `self: Arc<Self>` instead of `&self` where implementations may need to spawn or retain shared ownership during asynchronous listing, restoration, or multipart completion.

## State and Persistence Behavior

The traits do not store state. They define operations that mutate or inspect persistent state managed by implementors: bucket namespace, object metadata and content, multipart upload state, tags, replication/delete markers, transitioned objects, format healing, and locks. Types such as `ObjectOptions`, `ObjectInfo`, `FileInfo`, `ObjectToDelete`, `DeletedObject`, `MultipartUploadResult`, `PartInfo`, and `HealResultItem` carry the state contract across the boundary.

## Dependencies and Integration Points

The file imports from `super::*`, so it relies on the store API module prelude for all domain types and async support. It depends on `async_trait` for async methods in traits and on `Arc` for methods that need owned shared receivers. The primary integration points are S3 front-end handlers, erasure-backed storage implementations, metadata/lifecycle/replication subsystems, healing code, and namespace lock management.

## Risks and Edge Cases

- The unified API is broad; implementors must keep many operations behaviorally consistent around versioning, replication, lifecycle, and locking.
- Many methods accept `ObjectOptions`, which is a large option bag. Missing or misinterpreted flags can cause subtle behavior differences between implementations.
- `delete_objects` returns per-object errors as `Vec<Option<Error>>`, so callers must preserve positional alignment with input objects.
- `copy_object_part` and `copy_object` have many arguments and depend on matching source/destination options correctly.
- `StorageAPI` does not include `NamespaceLocking`, so consumers that require lock creation must request that trait separately.

## Test Signals

There are no tests in this file because it is purely trait definitions. Behavioral coverage must come from concrete implementors and integration tests that exercise bucket/object/list/multipart/heal paths through these contracts.
