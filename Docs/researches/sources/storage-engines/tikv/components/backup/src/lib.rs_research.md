# sources/storage-engines/tikv/components/backup/src/lib.rs

## Purpose
This is the crate root for TiKV’s `backup` component. It declares the module graph, enables a nightly feature required by nested boxed error pattern matching, wires allocator support, and reexports the public backup API surface.

## Important APIs, Types, And Functions
The crate exposes modules `disk_snap`, `endpoint`, `errors`, `metrics`, `service`, `softlimit`, `utils`, and `writer`. Public reexports include `Endpoint`, `Task`, `backup_file_name`, `storage_backend_config`, `Error`, `Result`, `Service`, `BackupRawKvWriter`, and `BackupWriter`.

## Control Flow
There is no runtime control flow in this file. It determines which internal modules compile and which types/functions downstream crates can import directly from `backup`.

## State And Persistence Behavior
No state or persistence is implemented here. It enables allocator linkage through `tikv_alloc` and exposes modules that own backup state, storage writing, metrics, and service wiring.

## Dependencies And Integration Points
The crate root is the integration point for TiKV/BR code importing backup endpoint and service functionality. `#![feature(box_patterns)]` supports `errors.rs` conversions that destructure boxed nested errors.

## Risks And Edge Cases
The nightly feature makes the crate toolchain-sensitive. Only selected endpoint/error/service/writer items are reexported; consumers needing lower-level utilities must use module paths or add exports.

## Test Signals
No tests live in this file. Its behavior is validated indirectly by successful compilation and tests of the reexported endpoint/service/writer modules.
