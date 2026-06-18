# File Research: sources/teaching/minix/minix/fs/mfs/glo.h

`glo.h` declares MFS service globals using the `EXTERN` pattern: variables are declarations normally, but become definitions when `_TABLE` is defined by `table.c`.

The globals include `err_code` for temporary error propagation, `cch[NR_INODES]` for disabled inode reference diagnostics in `main.c`, `fs_dev` for the single mounted device handled by the service instance, and `used_zones` for statvfs/block-usage accounting. It also declares the exported fsdriver dispatch table `mfs_table`.
