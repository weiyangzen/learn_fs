# File Research: sources/os/linux/linux/fs/file.c

Read status: complete, 1531 lines.

Purpose: manages per-process file descriptor tables: allocation, expansion, cloning, fd installation, close/close_range, fd lookup, dup/dup2/dup3, close-on-exec, and descriptor iteration.

Key flow:
- File reference slowpath `__file_ref_put()` handles last-reference transition to `FILE_REF_DEAD`, saturated counts, and imbalanced puts.
- `alloc_fdtable()`, `expand_fdtable()`, and `expand_files()` grow fd arrays and bitmaps while coordinating with lockless `fd_install()` via `resize_in_progress`, RCU grace periods, and barriers.
- `dup_fd()` clones a `files_struct`, optionally punching a `close_range()` hole, and handles reserved-but-uninstalled fd slots by clearing them in the clone.
- `alloc_fd()`, `get_unused_fd_flags()`, `fd_install()`, `put_unused_fd()`, and `file_close_fd_locked()` maintain open fd bitmaps, close-on-exec bitmaps, and pointer table invariants.
- `close_range()` supports close, cloexec marking, and optional unshare of shared descriptor tables.
- `__fget_files_rcu()`, `fget()`, `fdget()`, and `fdget_pos()` implement RCU-safe fd lookup, optional borrowed references for unshared tables, and f_pos locking for shared atomic-position files/directories.
- `replace_fd()`, `receive_fd()`, `ksys_dup3()`, `dup2()`, `dup()`, and `f_dupfd()` implement descriptor replacement and duplication.

Important dependencies: `fdtable`, RCU, `file_ref`, process `files_struct`, `RLIMIT_NOFILE`, socket receive hooks, LSM receive checks, `close_range` flags.

Risk/concurrency notes:
- The file is highly sensitive to RCU ordering and SLAB_TYPESAFE_BY_RCU reuse; pointer reloads and refcount acquisition must remain paired.
- `fd_install()` assumes a descriptor slot has been reserved and still contains NULL.
- `do_dup2()` explicitly returns `-EBUSY` for races with a reserved-but-not-installed target fd.
