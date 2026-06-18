# sources/security-integrity/cryfs/crates/cryfs-filesystem/src/filesystem/node.rs

## Purpose
Implements `CryNode`, the generic RustFS node adapter that dispatches a CryFS blob-backed node into directory, file, or symlink adapters and exposes shared attribute operations.

## Important APIs, types, and functions
- `CryNode::new` wraps a `NodeInfo` into `AsyncDropArc`; `new_internal` accepts an already shared `NodeInfo`.
- `load_blob` delegates to `NodeInfo`.
- The `Node` trait impl provides `as_dir`, `as_symlink`, `as_file`, `getattr`, `setattr`, and test-only `fsync`.
- `AsyncDrop` releases `node_info` and the blobstore guard.

## Control flow
Type conversion is based on `NodeInfo::node_type`, avoiding blob loads on the happy path. If the type matches, the node clones the blobstore and `NodeInfo` into the specialized adapter; if it does not match, it returns RustFS type errors. Attribute operations are forwarded directly to `NodeInfo`.

## State and persistence behavior
`CryNode` keeps shared runtime references to the blobstore and node metadata. It does not mutate persistence except through forwarded `setattr` and test-only `fsync`, which can flush the blob and parent metadata.

## Dependencies and integration points
Connects `CryDir`, `CryFile`, `CrySymlink`, `NodeInfo`, `ConcurrentFsBlobStore`, `BlobType`, and the RustFS `Node` trait. RustFS inode caching can reuse this node, so `NodeInfo` is intentionally arc-shared.

## Risks and edge cases
`as_file` maps symlink-as-file to `UnknownError` with a TODO, which may produce poor POSIX error fidelity. The test-only `fsync` duplicates logic from directory/open-file fsync. Incorrect `NodeInfo` entry type can delay corruption detection until the specialized adapter loads and casts the blob.

## Test signals
Useful signals include type-dispatch tests for dir/file/symlink nodes, getattr/setattr forwarding, symlink-as-file error behavior, and inode-cache reuse of shared `NodeInfo`.
