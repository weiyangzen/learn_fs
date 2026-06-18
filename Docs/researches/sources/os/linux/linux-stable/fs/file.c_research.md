# File Research: sources/os/linux/linux-stable/fs/file.c

This file manages per-process file descriptor tables (`struct files_struct` and `struct fdtable`) and the fd-oriented APIs used by open, close, dup, exec, SCM_RIGHTS, pidfd, and syscall fast paths.

Major responsibilities:
- Implement the `file_ref_t` slowpath for safe `struct file` refcount release and saturation/dead-state handling.
- Allocate, expand, duplicate, and free dynamic fd tables and their bitmaps.
- Track open fd bits, close-on-exec bits, full bitmap words, and `next_fd`.
- Allocate fd slots via `get_unused_fd_flags()` and release reserved slots via `put_unused_fd()`.
- Publish files into reserved slots with `fd_install()` while coordinating with concurrent fdtable resize.
- Close individual fds, ranges of fds, and close-on-exec descriptors.
- Provide RCU-safe file lookup helpers: `fget()`, `fget_raw()`, `fdget()`, `fdget_pos()`, task fd lookup, and iteration.
- Implement `dup`, `dup2`, `dup3`, `f_dupfd()`, and fd replacement.
- Install received files from other processes through `receive_fd()` and `receive_fd_replace()`.

Important design points:
- Small fd tables are embedded in `files_struct`; larger tables are allocated separately and freed after RCU grace periods.
- Bitmap sizes are aligned to `BITS_PER_LONG`, and `full_fds_bits` accelerates finding free descriptors.
- `resize_in_progress` coordinates lockless `fd_install()` with fdtable expansion.
- `dup_fd()` handles fd slots that are allocated but not yet populated, preserving the invariant that reserved slots contain `NULL` until `fd_install()`.
- RCU lookup handles `SLAB_TYPESAFE_BY_RCU` reuse by refcounting first, then rechecking the fdtable pointer and slot.
- `fdget()` can borrow a file without taking a ref when the files table is unshared; otherwise it falls back to a normal refcounted lookup.
- `fdget_pos()` conditionally locks `f_pos_lock` for shared seek position correctness.

Key invariants:
- `files->file_lock` protects fd allocation, bitmap mutation, close, dup target replacement, and fdtable replacement.
- A successfully reserved fd has `open_fds` set and `fd[fd] == NULL` until `fd_install()`.
- `fd_install()` consumes the caller's file reference.
- `dup2`/`dup3` return `-EBUSY` if the target fd is reserved but not populated.
- `close_range(CLOSE_RANGE_UNSHARE)` may clone the fdtable with a punched-out closed range before installing it on the task.
- RCU readers must validate that the file pointer and fdtable did not change after acquiring a file reference.

External interfaces:
- Exports fd allocation/installation/closing/lookup APIs, `close_range`, `dup`, `dup2`, `dup3`, `receive_fd`, `iterate_fd`, and file position locking helpers.
