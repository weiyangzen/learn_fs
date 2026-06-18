<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/dirent64.c -->
## sources/test-tools/strace/src/dirent64.c

Purpose: Decodes `getdents64`.

Important APIs and types: `kernel_dirent64_t`, `print_dentry_head`, `decode_dentry_head`, `decode_dentry_tail`, and `SYS_FUNC(getdents64)`.

Control flow: `getdents64` delegates to `xgetdents` with a header size ending at `d_name`. The head callback prints inode, offset, and record length outside abbrev mode. The tail callback prints symbolic `d_type`, then a capped directory name.

State and persistence: No persistent state.

Dependencies and integration: Depends on `xgetdents.h`, `kernel_dirent.h`, `dirent_types`, path printing, and generic memory fetches.

Risks: Name length is bounded to 256 for output, so unusually long or malformed entries are abbreviated. Correctness relies on `xgetdents` record traversal.

Test signals: Tests should include ordinary and long filenames, all common `DT_*` types, abbrev mode, and truncated buffers.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/dirent64.c -->
