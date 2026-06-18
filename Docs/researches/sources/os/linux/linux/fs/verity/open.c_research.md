# File Research: sources/os/linux/linux/fs/verity/open.c

## Purpose
Loads, validates, creates, caches, and cleans up per-inode fs-verity metadata when verity files are opened or enabled.

## Main Functions
- Tree parameter setup:
  - `fsverity_init_merkle_tree_params()`: validates hash algorithm/block size, computes Merkle tree levels, level offsets, size, page count, zero-block digest, and optional salted state.
- Descriptor/info creation:
  - `compute_file_digest()`: hashes descriptor excluding builtin signature and with `sig_size` zeroed.
  - `fsverity_create_info()`: allocates `fsverity_info`, initializes tree params, copies root hash, computes file digest, verifies signature, and allocates hash-block bitmap when needed.
- Info cache:
  - `fsverity_set_info()`: inserts info into rhashtable.
  - `__fsverity_get_info()`: looks up cached info by inode pointer.
  - `fsverity_free_info()`, `fsverity_remove_info()`, `fsverity_cleanup_inode()`: lifetime cleanup.
  - `fsverity_init_info_cache()`: initializes rhashtable and usercopy-safe kmem cache.
- Descriptor loading:
  - `validate_fsverity_descriptor()`: checks size, version, reserved bits, salt size, inode size match, and signature bounds.
  - `fsverity_get_descriptor()`: obtains descriptor size and contents via filesystem `get_verity_descriptor()`.
- Open hook:
  - `ensure_verity_info()`: loads and caches metadata, handling races where another opener inserted it first.
  - `__fsverity_file_open()`: rejects writable opens and ensures metadata is loaded.

## Important Design Points
- Merkle block size must be power-of-two, at least 1024, no larger than page size, and no larger than filesystem block size.
- Tree level order stores root level first in the tree area and leaf level last; `level_start[]` maps logical level to start block.
- Bitmap for verified hash blocks is capped indirectly to avoid excessive memory.
- Descriptor `data_size` must exactly match current inode size.
- Multiple racing openers can create duplicate `fsverity_info`; the loser frees its copy after rhashtable insertion race resolution.
- Cache lookup is guarded by `S_VERITY` in public helpers, while internal insertion can happen before final flag setting during enable.

## Cross-File Relationships
- Uses hash support from `hash_algs.c` and signature support from `signature.c`.
- Called by `enable.c`, `measure.c`, `read_metadata.c`, and filesystems through exported open/cleanup helpers.
- Requires filesystem `get_verity_descriptor()` operation.

## Risks / Review Notes
- Inode-pointer keyed rhashtable requires reliable cleanup at inode eviction.
- Tree size computations must avoid overflow and remain within `ULONG_MAX` page/hash block indexing.
- Descriptor validation is a security boundary; accepting mismatched size or reserved bits would weaken ABI guarantees.
