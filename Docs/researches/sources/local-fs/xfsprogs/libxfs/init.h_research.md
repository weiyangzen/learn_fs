# File Research: sources/local-fs/xfsprogs/libxfs/init.h

Small initialization header.

Key responsibilities:
- Declares global `use_xfs_buf_lock`.
- Forward-declares `struct stat`.

Dependencies:
- Included by libxfs implementation files that need global buffer-lock mode.

Notable risks:
- Most libxfs init interfaces are declared elsewhere; this header is intentionally narrow.
