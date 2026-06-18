# File Research: sources/os/linux/linux-stable/fs/verity/enable.c

Implements `FS_IOC_ENABLE_VERITY`. It validates the userspace enable argument, requires a writable-permitted regular file opened for read, rejects append-only/directories/non-regular files, obtains mount write access, and uses `deny_write_access()` to stabilize file contents while building the Merkle tree.

`build_merkle_tree()` hashes file data blocks, accumulates digest blocks per tree level, writes complete Merkle tree blocks through the filesystem’s `write_merkle_tree_block()` operation, handles zero-length files specially with an all-zero root hash, and aborts on fatal signals.

`enable_verity()` builds a descriptor with algorithm, block size, salt, optional builtin signature, file size, and root hash. It calls filesystem `begin_enable_verity()`, builds the tree outside the inode lock, creates and caches `fsverity_info`, then calls `end_enable_verity()` to persist metadata and set `S_VERITY`. On failure it rolls back through `end_enable_verity(filp, NULL, ...)`.

The code deliberately does not drop pagecache after enable, documenting the tradeoff between a narrow race and performance.
