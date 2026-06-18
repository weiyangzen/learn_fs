# File Research: sources/os/linux/linux-stable/fs/verity/open.c

Handles open-time loading and caching of fs-verity metadata. It maintains a global rhashtable keyed by inode pointer and a slab cache for `fsverity_info`.

`fsverity_init_merkle_tree_params()` validates algorithm and log block size, prepares salted hash state, computes hashes per block, number of tree levels, per-level starting blocks, tree size, and tree pages. It enforces block size constraints: power-of-two, 1 KiB minimum, no larger than page size or filesystem block size, and not too small for the digest.

`fsverity_create_info()` builds cached verification state from a descriptor, computes the file digest over the descriptor with signature omitted, verifies optional builtin signature, and allocates a verified-hash-block bitmap when Merkle block size differs from page size. `fsverity_get_descriptor()` asks the filesystem for descriptor size/content and validates version, reserved fields, salt size, data size, and signature bounds.

`__fsverity_file_open()` rejects write opens and ensures verity info is cached. `fsverity_cleanup_inode()` removes cached state at inode cleanup.
