# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/file.rs

## Purpose
Defines `CryFile`, the lightweight closed-file adapter that can be converted into a `CryOpenFile` for read/write operations.

## Important APIs, types, and functions
- `CryFile::new` stores a borrowed blobstore guard and shared `NodeInfo`.
- The `File` trait impl exposes `into_open`, returning `CryOpenFile`.
- `Debug` prints `node_info`; `AsyncDrop` drops the `NodeInfo` guard.

## Control flow
The adapter does not load or validate file contents itself. `into_open` consumes the async-drop guard with `unsafe_into_inner_dont_drop`, clones the shared blobstore arc, transfers the `NodeInfo` guard, and constructs an open-file adapter. Open flags are accepted but currently ignored.

## State and persistence behavior
`CryFile` owns no persistent state. It keeps the parent/entry metadata reachable through `NodeInfo`; persistence work is delegated to `CryOpenFile` and `NodeInfo`.

## Dependencies and integration points
Integrates the RustFS `File` trait with `CryOpenFile`, `CryDevice`, `NodeInfo`, `ConcurrentFsBlobStore`, and CryFS async-drop ownership.

## Risks and edge cases
Ignoring `OpenInFlags` means access mode, append, truncate, and similar semantics are not enforced here. The TODO notes potential missed sharing of cached metadata between `CryFile` and `CryOpenFile`.

## Test signals
Coverage should verify that opening a looked-up file yields a usable `CryOpenFile`, that dropped file handles release metadata guards, and that open flags are either implemented elsewhere or intentionally unsupported.
