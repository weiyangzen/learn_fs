# File Research: sources/os/linux/linux/fs/coda/dir.c

Coda directory inode/file/dentry operations. This file forwards namespace operations to Venus, maintains local VFS dentry/inode state, supports fallback Venus directory entry format, and handles Coda invalidation flags.

Directory operations:
- `coda_lookup()`: validates name length, creates `.CONTROL` inode at root, otherwise calls `venus_lookup()` and instantiates result.
- `coda_permission()`: non-RCU permission check with execute bit validation, minicache lookup, Venus access upcall, and cache insert on success.
- `coda_create()`, `coda_mkdir()`, `coda_link()`, `coda_symlink()`: forward creation/link operations to Venus and update local inode/dentry/link/mtime state.
- `coda_unlink()`, `coda_rmdir()`: forward removals to Venus and update local link counts/mtime.
- `coda_rename()`: rejects nonzero flags, calls Venus rename, updates link counts for directory replacement and flags overwritten inode attributes stale.
- `.mknod` is wired to an EIO-returning stub.

Directory read:
- `coda_readdir()` first tries `iterate_dir()` on the host/container file.
- If that returns `-ENOTDIR`, `coda_venus_readdir()` reads Venus-format `struct venus_dirent` records from the container file.
- Fallback parser emits dots, validates short/truncated records, skips `.` and `..`, maps Coda d_type to Linux `DT_*`, and advances by `d_reclen`.

Dentry/inode invalidation:
- `coda_dentry_revalidate()` rejects RCU walk, checks `C_PURGE`/`C_FLUSH`, shrinks child dcache, propagates flush flags, and invalidates unused dentries.
- `coda_dentry_delete()` asks VFS to drop dentries whose inode has `C_PURGE`.
- `coda_revalidate_inode()` refetches attributes when Coda flags indicate stale/purge/flush, warns on type changes, rejects inode-number changes, propagates child flush, and clears flags.

Registered ops:
- `coda_dentry_operations`
- `coda_dir_inode_operations`
- `coda_dir_operations`

Notable behavior:
- `.CONTROL` cannot be created/linked as a normal root entry.
- Directory link count helpers deliberately avoid changing ambiguous low link counts used by Coda/Venus tricks for volume mount points.
