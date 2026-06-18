# File Research: sources/os/linux/linux/fs/verity/enable.c

## Purpose
Implements `FS_IOC_ENABLE_VERITY`: validates userspace enable arguments, builds the Merkle tree for a file, creates fs-verity metadata, and asks the filesystem to commit verity enablement.

## Main Functions
- Merkle construction:
  - `hash_one_block()`: zero-pads a partial block, hashes it, and appends digest into the next tree level buffer.
  - `write_merkle_tree_block()`: calls filesystem `write_merkle_tree_block()` operation.
  - `build_merkle_tree()`: reads file data, hashes data blocks upward through tree buffers, writes tree blocks, and returns root hash.
- Enable flow:
  - `enable_verity()`: creates descriptor, copies salt/signature, initializes tree params, calls filesystem begin/end hooks, builds tree, creates/caches `fsverity_info`, and rolls back on error.
  - `fsverity_ioctl_enable()`: validates ioctl args, permissions, file type, read mode, append flag, mount writability, and denies concurrent writes before calling `enable_verity()`.

## Important Design Points
- Empty files have an all-zero root hash special case.
- Merkle tree blocks are written through filesystem-specific storage hooks, but tree contents are filesystem-independent.
- `deny_write_access()` stabilizes file data while hashing.
- Inode lock serializes `begin_enable_verity()` and `end_enable_verity()`, but is not held during long tree construction.
- Descriptor is re-read through `fsverity_create_info()` validation logic before final commit.
- `fsverity_set_info()` occurs before `end_enable_verity()`; other users still require `S_VERITY`, which filesystem sets at the end.
- Rollback calls `end_enable_verity(filp, NULL, 0, tree_size)`.

## Cross-File Relationships
- Uses hash and tree parameter helpers from `hash_algs.c` and `open.c`.
- Uses `fsverity_create_info()`, `fsverity_set_info()`, `fsverity_remove_info()`.
- Requires filesystem `s_vop` methods: `begin_enable_verity`, `write_merkle_tree_block`, and `end_enable_verity`.

## Risks / Review Notes
- Filesystem hooks must maintain ordering: `S_VERITY` should be set only at the end of successful `end_enable_verity()`.
- A short read while building the tree is treated as corruption/logic failure.
- The code intentionally no longer drops pagecache after enabling, accepting a small residual race tradeoff documented in comments.
