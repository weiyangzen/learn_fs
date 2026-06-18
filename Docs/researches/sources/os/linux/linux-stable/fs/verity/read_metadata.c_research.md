# File Research: sources/os/linux/linux-stable/fs/verity/read_metadata.c

Implements `FS_IOC_READ_VERITY_METADATA`. It supports reading three byte-stream metadata types from a verity file: Merkle tree, descriptor, and builtin signature.

`fsverity_read_merkle_tree()` bounds the requested range to the tree size, optionally triggers filesystem Merkle-tree readahead, then reads each Merkle tree page with `read_merkle_tree_page()`, maps it, and copies requested bytes to userspace. It handles signals and returns partial progress when available.

`fsverity_read_descriptor()` loads the descriptor, clears `sig_size`, and exposes only the fixed descriptor without the builtin signature. `fsverity_read_signature()` exposes just the builtin signature and returns `-ENODATA` if none exists. The ioctl validates reserved fields and offset overflow, clamps length to `INT_MAX`, and dispatches by metadata type.
