# sources/user-network-fs/libfuse/example/passthrough_ll.c

## Purpose
`passthrough_ll.c` is a low-level C passthrough filesystem that mirrors a source directory, defaulting to `/`. It is more explicit than the high-level variants: it maintains an inode table, maps FUSE node IDs to `struct lo_inode *`, uses directory handles, supports configurable cache modes, writeback, flock, and optional xattrs.

## Important APIs, Types, and Functions
Core types are `struct lo_inode` and `struct lo_data`. `lo_inode` stores linked-list pointers, a backing `fd`, source inode/device IDs, and a mutex-protected refcount. `lo_data` stores global options, timeouts, cache mode, source path, and root inode. `lo_opts` parses `writeback`, `source=`, `flock`, `xattr`, `timeout=`, and `cache=` mount options. The operation table `lo_oper` registers low-level handlers for lookup, create, tmpfile, read/write buffers, metadata, directory operations, forget, xattrs, locks, copy, lseek, and statx.

## Control Flow
`main()` parses libfuse command-line options, parses custom options into `lo`, validates and opens the source directory with `O_PATH`, creates a low-level session, mounts it, daemonizes, and runs the selected loop. `lo_do_lookup()` opens a child relative to its parent fd, stats it, reuses an existing `lo_inode` by `(ino,dev)` if present, or creates a new linked-list entry. `lo_forget()` and `lo_forget_multi()` decrement refcounts and free inode records when no kernel lookups remain. File and directory operations mostly use `openat`, `fstatat(AT_EMPTY_PATH)`, `/proc/self/fd`, and FD-backed `fuse_bufvec`.

## State and Persistence
Persistent state is all backing filesystem content. Runtime state is the linked list of known inodes and their open `O_PATH` fds, root fd, directory stream handles, and per-open file fds in `fi->fh`. Cache timeout derives from `cache=never|auto|always` unless explicitly set. `cache=never` sets direct I/O, `cache=always` sets keep-cache, and normal cache uses a one-second timeout.

## Dependencies and Integration Points
This file depends on low-level libfuse, pthread mutexes, Linux `AT_EMPTY_PATH`, `/proc/self/fd`, xattr APIs, `flock`, and helper functions in `passthrough_helpers.h`. It negotiates `FUSE_CAP_WRITEBACK_CACHE` and `FUSE_CAP_FLOCK_LOCKS`. It integrates with readdirplus by performing lookups for directory entries and manually forgetting entries that do not fit into the response buffer.

## Risks
Pointer-valued inode IDs must match the lifetime of allocated `lo_inode` records; incorrect refcount/forget behavior would create use-after-free. `create_new_inode()` can return NULL, but `fill_entry_param_new_inode()` casts the result to an inode without checking, so memory pressure can produce an invalid zero inode path. Some operations use `/proc/self/fd`, making Linux semantics important despite limited portability. Writeback cache changes O_WRONLY to O_RDWR and strips O_APPEND, accepting append atomicity loss.

## Test Signals
Mount with `source=<tmpdir>` and run metadata, data, hardlink, readdirplus, create/tmpfile, xattr, flock, fallocate, copy-file-range, lseek, and statx tests. Vary `cache=never`, `cache=auto`, `cache=always`, `writeback`, and `no_writeback`. Use small readdir buffers to verify lookup count repair when entries do not fit.
