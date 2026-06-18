# sources/object-store/rustfs/crates/protocols/src/sftp/state.rs

## Purpose
`state.rs` defines the in-memory state machines used by SFTP driver operations. Operation logic lives in sibling modules; this file holds shared state shapes.

## Important APIs, Types, and Functions
`HandleState` is stored in the driver handle table. `File` contains bucket, key, size, attrs, and read cache. `Dir` wraps `DirCursor`. `Write` contains bucket, key, fstat attrs, raw open attrs, and `WritePhase`. `WritePhase` models `Buffering`, `Streaming`, and `Failed` multipart lifecycle. `CompletedPart` stores part number and ETag. `MultipartUpload` pairs upload id with cached abort authorization. `DirCursor` and `ListingContinuation` model root/bucket/prefix directory iteration.

## Control Flow
Read opens create `File`. Directory operations advance `DirCursor` and `ListingContinuation`. Writes begin in `Buffering`, transition to `Streaming` after multipart creation, append uploaded parts, and move to `Failed` on upload-part errors. Close completes or aborts according to phase.

## State and Persistence Behavior
All state is per-session in the handle table. `Streaming` and `Failed` hold persistent backend upload ids. `abort_authorized` is cached at create-multipart time so close and synchronous driver drop can decide cleanup without async IAM.

## Dependencies and Integration Points
The file depends on `ReadCache`, SFTP `FileAttributes`, and `s3s::dto::ETag`. It is used by driver, read, write, directory, and tests.

## Risks and Test Signals
Risks include invalid phase transitions, stale abort authorization, losing uploaded part order, and directory cursor cancellation-safety regressions. The local test pins S3 multipart constants; behavior is tested in mutating modules.
