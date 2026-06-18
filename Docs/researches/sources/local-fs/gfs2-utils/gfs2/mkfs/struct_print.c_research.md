# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.c

Debug printer for GFS2 on-disk structures. Callers pass raw on-disk buffers or struct pointers, and functions print big-endian fields converted to CPU order.

Key functions:
- `inum_print`
- `meta_header_print`
- `sb_print`
- `rindex_print`
- `rgrp_print`
- `quota_print`
- `dinode_print`
- `leaf_print`
- `log_header_print`
- `log_descriptor_print`
- `statfs_change_print`
- `quota_change_print`

Implementation uses `print_it` plus `printbe16`, `printbe32`, and `printbe64` macros.

Dependencies include `libgfs2`, endian conversion helpers, `uuid_unparse`, and standard printf formatting.

Research notes:
- `main_mkfs.c` uses `dinode_print`, `rindex_print`, and `statfs_change_print` in debug paths.
- These printers are diagnostic only and do not mutate metadata.
