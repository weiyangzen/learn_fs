# sources/object-store/rustfs/crates/ecstore/src/store_api.rs

## Purpose
This file is the public store API prelude for the ecstore crate. It centralizes imports, constants, submodules, and re-exports for bucket/object/storage types, reader utilities, traits, and API-facing type definitions used by `ECStore` and callers.

## Important APIs, Types, And Functions
- Constants: `ERASURE_ALGORITHM = "rs-vandermonde"` and `BLOCK_SIZE_V2 = 1 MiB`.
- Submodules: `readers`, `traits`, and `types`.
- Re-exports: `readers::*`, `traits::*`, `types::*`, plus storage API bucket option/info types (`BucketInfo`, `BucketOptions`, `DeleteBucketOptions`, `MakeBucketOptions`).
- Imports establish the API vocabulary for object metadata, replication, lifecycle, tiering, checksums, compression, HTTP headers, namespace locks, healing, and async readers.

## Control Flow
There is no executable control flow beyond module declarations and re-exports. The file shapes compilation and public API access by collecting dependencies and exposing submodule contents.

## State And Persistence Behavior
This file does not manage state or persistence. Its constants influence erasure metadata/chunking behavior in downstream code, and its re-exported types carry persistent metadata fields, but no runtime mutation occurs here.

## Dependencies And Integration Points
The file binds together `rustfs_storage_api`, `rustfs_filemeta`, lifecycle/transition modules, replication status helpers, restore status parsing, HTTP header constants, checksum/compression utilities, `NamespaceLockWrapper`, healing types, async I/O, UUIDs, and Tokio cancellation. It is a central dependency surface for the `store` module and external code importing ecstore store APIs.

## Risks And Edge Cases
- As a prelude-style module, unused or overly broad imports can hide coupling and increase rebuild surface.
- Public wildcard re-exports make API changes in `readers`, `traits`, or `types` immediately visible to downstream callers.
- Constants such as `ERASURE_ALGORITHM` and `BLOCK_SIZE_V2` are compatibility-sensitive; changing them would affect stored metadata expectations and object layout assumptions.
- Because many metadata/status helper imports are centralized here, changes can create subtle compile/API churn outside this file.

## Test Signals
No tests are defined in this file. Signal comes from compilation and downstream tests that import store API types or rely on erasure constants. API compatibility tests or crate-level public API checks would be the most relevant coverage.
