# File Research: sources/os/linux/linux/fs/9p/vfs_dir.c

Implements 9p directory file operations and directory FID release.

Key behavior:
- Defines `struct p9_rdir`, an on-demand per-FID directory read buffer.
- Legacy `v9fs_dir_readdir()` reads raw stat records with `p9_client_read()`, decodes them with `p9stat_read()`, and emits entries using QID-derived inode numbers.
- Dotl `v9fs_dir_readdir_dotl()` calls `p9_client_readdir()`, decodes `p9_dirent` records, and uses server-provided offsets and dtypes.
- `dt_type()` maps legacy 9p mode bits to `DT_REG`, `DT_DIR`, or `DT_LNK`.
- `v9fs_dir_release()`:
  - Flushes dirty regular-file mapping data on writable close.
  - Removes open FIDs from the inode FID list.
  - Drops the FID.
  - Unuses the FS-Cache cookie, updating coherency version and size for writable handles.
- Defines directory operations for legacy/u and dotl protocol variants.

Important interactions:
- Directory open is shared with regular files via `v9fs_file_open()`.
- Release is also used by regular file operations in `vfs_file.c`.
