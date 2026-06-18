# File Research: sources/os/linux/linux/fs/verity/fsverity_private.h

## Purpose
Private fs-verity subsystem header defining internal constants, hash/tree metadata structures, cached inode metadata, and internal function prototypes.

## Main Contents
- `FS_VERITY_MAX_LEVELS`: implementation limit of 8 Merkle levels.
- `struct fsverity_hash_alg`: supported hash algorithm metadata.
- `union fsverity_hash_ctx`: SHA-256/SHA-512 initial state storage.
- `struct merkle_tree_params`: hash algorithm, optional salted initial state, block/tree geometry, zero digest, and level start offsets.
- `struct fsverity_info`: rhashtable node, tree params, root hash, file digest, inode pointer, and optional hash-block verification bitmap.
- `FS_VERITY_MAX_SIGNATURE_SIZE`.
- Prototypes for hash algorithms, init/logging, BPF digest kfunc setup, open/info cache, descriptor loading, optional signature verification, and verify workqueue.
- Includes trace event definitions.

## Important Design Points
- `fsverity_info` is cached globally by inode pointer and remains until inode cleanup.
- Merkle tree pages are not stored in `fsverity_info`; filesystems may cache them separately.
- Hash block verification bitmap is only needed when Merkle block size differs from page size.

## Cross-File Relationships
- Included by every fs-verity C file.
- Bridges public `linux/fsverity.h` interfaces with subsystem internals.

## Risks / Review Notes
- `FS_VERITY_MAX_LEVELS`, digest sizes, and descriptor size limits are security/format constraints.
- Cached metadata lifetime depends on filesystems calling `fsverity_cleanup_inode()` when evicting inodes.
