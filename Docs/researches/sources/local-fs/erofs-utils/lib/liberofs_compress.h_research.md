# File Research: sources/local-fs/erofs-utils/lib/liberofs_compress.h

This internal compression header declares the interface between inode import and compressed-data construction.

Constants:
- `EROFS_CONFIG_COMPR_MAX_SZ` is 4000 KiB.
- `Z_EROFS_COMPR_QUEUE_SZ` is twice that max size.

Opaque type:
- `struct z_erofs_compress_ictx` represents per-file compression context.

File compression API:
- `erofs_prepare_compressed_file()`
- `erofs_bind_compressed_file_with_fd()`
- `erofs_begin_compressed_file()`
- `erofs_write_compressed_file()`
- `z_erofs_drop_inline_pcluster()`

Directory compression API:
- `erofs_begin_compress_dir()`
- `erofs_write_compress_dir()`

Lifecycle:
- `z_erofs_compress_init()`
- `z_erofs_compress_exit()`
- `z_erofs_mt_global_exit()`

Known users:
- `importer.c` initializes compression.
- `inode.c` prepares/begins/writes compressed files and directories, with fallback to unencoded output on `-ENOSPC`.

Risk / note:
- The API separates “begin” from “write”, enabling async job scheduling, so callers must keep fd/context lifetime valid across both phases.
