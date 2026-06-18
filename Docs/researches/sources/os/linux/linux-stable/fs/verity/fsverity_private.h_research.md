# File Research: sources/os/linux/linux-stable/fs/verity/fsverity_private.h

Private fs-verity subsystem header. It defines implementation limits and core private types: `FS_VERITY_MAX_LEVELS`, `fsverity_hash_alg`, `union fsverity_hash_ctx`, `merkle_tree_params`, and `fsverity_info`.

`merkle_tree_params` captures hash algorithm, salted initial hash state, digest/block sizes, arity, tree depth, total tree size/pages, and per-level block offsets. `fsverity_info` is the cached per-inode verification state stored in a global rhashtable and includes root hash, file digest, inode pointer, and optional hash-block verified bitmap.

The header declares internal helpers for hashing, initialization, descriptor loading, info-cache management, signature verification, BPF registration, verification workqueue setup, and tracepoint inclusion. It also provides logging wrappers `fsverity_warn()` and `fsverity_err()`.
