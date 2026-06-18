# File Research: sources/os/linux/linux-stable/fs/internal.h

This header declares internal VFS interfaces shared among files under `fs/`. It is not a public filesystem API; it connects namespace, namei, file table, superblock, inode, dcache, xattr, stat, splice, mount-idmap, and namespace filesystem internals.

Key responsibilities:
- Declares internal init hooks such as `bdev_cache_init()`, `chrdev_init()`, `filename_init()`, and `mnt_init()`.
- Declares internal namei helpers for lookup, mkdir, mknod, symlink, link, unlink, rmdir, rename, tmpfile, and no-permission lookup paths.
- Declares namespace and mount helpers: `path_mount()`, `path_umount()`, `path_pivot_root()`, `lookup_mnt()`, `finish_automount()`, and mount write-access helpers.
- Provides read-only remount synchronization helpers `sb_start_ro_state_change()` and `sb_end_ro_state_change()` with explicit memory barriers.
- Declares file table helpers for empty/backing file allocation and close/fput variants.
- Provides inline write-access release helpers `file_put_write_access()` and `put_file_access()`.
- Declares inode, writeback, dcache, pipe, fs pin, nsfs, stat, splice, xattr, idmap, stashed dentry, anon inode, pidfs, and nsfs internal hooks.
- Defines internal structures such as `open_flags`, `xattr_name`, `kernel_xattr_ctx`, and `stashed_operations`.
- Provides `path_mounted()` helper to identify mount roots.

Important interactions:
- Used by `fs/init.c`, `fs/ioctl.c`, `fs/inode.c`, and many other VFS implementation files.
- Bridges otherwise separate VFS implementation units while avoiding public exposure in `include/linux/fs.h`.

Notable invariants and risks:
- Memory barriers in `sb_start_ro_state_change()` and `sb_end_ro_state_change()` pair with mount read-only checks and write-access acquisition paths.
- Helpers in this header are internal contracts; changing prototypes or semantics can cascade across core VFS code.
- `put_file_access()` encodes mode-specific release behavior for read counts, writers, and backing files.

Research notes:
- This header is best understood as the VFS private linkage surface. It reveals subsystem boundaries and dependency directions inside `fs/`.
