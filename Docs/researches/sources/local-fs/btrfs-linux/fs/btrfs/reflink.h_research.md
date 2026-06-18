# File Research: sources/local-fs/btrfs-linux/fs/btrfs/reflink.h

This small header declares the Btrfs remap/reflink VFS entry point.

Interface:
- Forward-declares `struct file`.
- Declares `loff_t btrfs_remap_file_range(struct file *file_in, loff_t pos_in, struct file *file_out, loff_t pos_out, loff_t len, unsigned int remap_flags);`.

Cross-file relationships:
- `reflink.c` implements the function.
- `file.c` includes this header and assigns the function to `btrfs_file_operations.remap_file_range`.

Important invariants:
- The header keeps reflink internals private; callers only see the VFS-compatible remap signature.
- All validation, locking, clone/dedupe behavior, and sync semantics live in `reflink.c`.
