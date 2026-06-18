# File Research: sources/os/linux/linux/io_uring/fs.c

## Purpose
Implements io_uring filesystem namespace mutation opcodes: rename, unlink/rmdir, mkdir, symlink, and hardlink.

## Main Functions
- Rename:
  - `io_renameat_prep()`
  - `io_renameat()`
  - `io_renameat_cleanup()`
- Unlink/rmdir:
  - `io_unlinkat_prep()`
  - `io_unlinkat()`
  - `io_unlinkat_cleanup()`
- Mkdir:
  - `io_mkdirat_prep()`
  - `io_mkdirat()`
  - `io_mkdirat_cleanup()`
- Symlink:
  - `io_symlinkat_prep()`
  - `io_symlinkat()`
- Hardlink:
  - `io_linkat_prep()`
  - `io_linkat()`
  - `io_link_cleanup()`

## Important Design Points
- Operations reject fixed-file requests because they operate on directory fds and pathnames rather than a request file.
- Pathnames are captured with `delayed_getname()` / `delayed_getname_uflags()` and completed at issue time with `CLASS(filename_complete_delayed, ...)`.
- All namespace operations force async execution and set `REQ_F_NEED_CLEANUP` after pathname capture.
- Cleanup functions dismiss delayed filenames if the request does not reach normal issue completion.

## Cross-File Relationships
- Declared in `fs.h`.
- Uses filename-based VFS helpers from `../fs/internal.h`.
- Depends on delayed filename machinery declared in `include/linux/fs.h`.

## Risks / Review Notes
- Error paths must dismiss any delayed filename already acquired.
- Normal issue paths clear `REQ_F_NEED_CLEANUP`; cleanup paths must remain paired with prep state.
- `io_unlinkat_prep()` only allows `AT_REMOVEDIR` in flags.
