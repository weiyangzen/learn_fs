# File Research: sources/local-fs/ocfs2-tools/mount.ocfs2/xmalloc.c

Checked allocation and fatal error helpers.

`die()` prints a formatted error, invokes optional `at_die`, and exits. `xmalloc()`, `xrealloc()`, and `xstrdup()` wrap libc allocation and terminate with `EX_SYSERR` on allocation failure; `xmalloc(0)` returns `NULL`.
