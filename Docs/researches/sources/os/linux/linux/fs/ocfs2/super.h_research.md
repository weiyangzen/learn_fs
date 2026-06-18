# File Research: sources/os/linux/linux/fs/ocfs2/super.h

## Purpose

`super.h` declares OCFS2 superblock-level error/abort helpers and signal mask helpers used outside `super.c`.

## API Surface

- `__ocfs2_error(struct super_block *sb, const char *function, const char *fmt, ...)`
  - `__printf(3, 4)` annotated.
  - Wrapped by `ocfs2_error(sb, fmt, ...)`, which passes `__PRETTY_FUNCTION__`.
- `__ocfs2_abort(struct super_block *sb, const char *function, const char *fmt, ...)`
  - `__printf(3, 4)` annotated.
  - Wrapped by `ocfs2_abort(sb, fmt, ...)`.
- `ocfs2_block_signals(sigset_t *oldset)`
- `ocfs2_unblock_signals(sigset_t *oldset)`

## Correctness Notes

- The macros preserve caller function names in corruption/abort logs without each caller passing its function manually.
- Signal helpers are documented as void because in-kernel `sigprocmask()` only fails for invalid signal constants, which these wrappers do not use.
