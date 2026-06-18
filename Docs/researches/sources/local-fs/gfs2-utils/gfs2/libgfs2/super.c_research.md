# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/super.c

This file reads and validates the GFS2 superblock and rindex.

Public APIs:
- `lgfs2_check_sb()`
- `lgfs2_read_sb()`
- `lgfs2_rindex_read()`

Behavior:
- Validates superblock magic/type and a broad filesystem format range.
- Reads the superblock from the fixed GFS2 location.
- Populates in-core superblock fields and recomputes block-size-derived constants.
- Computes file and journal metadata height tables.
- Sets filesystem size from device fd length.
- Reads rindex file entries, inserts resource groups into `sdp->rgtree`, checks ordering/sanity, computes bit structures, and reports whether the rindex appears consistent.

Risk notes:
- `lgfs2_check_sb()` accepts fs format up to 1899 while `LGFS2_FS_FORMAT_VALID` uses a tighter range elsewhere.
- `lgfs2_read_sb()` assumes `lgfs2_bread()` succeeds before dereferencing.
- Rindex consistency checking may continue after bad entries by guessing next address from prior resource group.
- `good_on_disk()` trusts reading the expected rgrp block and only checks metadata type.
