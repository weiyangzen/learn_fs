# File Research: sources/local-fs/xfsprogs/libxfs/buf_mem.h

Header for memory-backed libxfs buffer targets.

Key responsibilities:
- Declares xmbuf block size/shift globals and lifecycle functions.
- Provides `xfs_buftarg_is_mem`.
- Declares daddr verification, transaction detach, finalization, and byte-count helpers.

Dependencies:
- Depends on `xfile` and libxfs buffer/transaction types.

Notable risks:
- `xfs_buftarg_is_mem` treats non-NULL `bt_xfile` as the complete discriminator for memory targets.
