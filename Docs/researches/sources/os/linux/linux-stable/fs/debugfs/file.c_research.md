# File Research: sources/os/linux/linux-stable/fs/debugfs/file.c

## Purpose

`file.c` implements debugfs file-operation safety wrappers and convenience file creators for common scalar, boolean, string, blob, array, register-set, and device-managed seqfile debug files.

## Main Responsibilities

- Provides noop file operations used when a debugfs file has no real operations.
- Exposes `debugfs_get_aux()` for retrieving auxiliary data stored in the debugfs inode.
- Implements active-user lifetime tracking with `debugfs_file_get()` and `debugfs_file_put()`.
- Provides cancellation registration for long-running debugfs handlers during removal.
- Enforces kernel lockdown restrictions for debugfs access.
- Defines open-only and full proxy file operations that safely call real debugfs handlers.
- Provides typed helper creators: `debugfs_create_u8/u16/u32/u64/ulong`, hex variants, `size_t`, `atomic_t`, bool, string, blob, u32 array, regset32, and device-managed seqfile.

## Core Data Flow

File access protection:
- `__debugfs_file_get()` lazily creates `struct debugfs_fsdata`, records available methods, and increments `active_users`.
- If a dentry has been unlinked or active users are draining, it returns `-EIO`.
- `debugfs_file_put()` decrements `active_users` and completes `active_users_drained` when the last protected user exits.

Proxy operations:
- `open_proxy_open()` protects only open, obtains module fops via `fops_get()`, replaces file fops, and calls real open.
- `debugfs_full_proxy_file_operations` keeps all main operations behind `debugfs_file_get()`/`put()`.
- `debugfs_full_short_proxy_file_operations` adapts `struct debugfs_short_fops` for llseek/read/write only.
- Full proxy release always calls real release without removal protection to avoid leaking per-open resources.

Typed attributes:
- Numeric helpers use `DEFINE_DEBUGFS_ATTRIBUTE` or signed variants, with mode selection between rw/ro/wo fops.
- Boolean helpers print `Y\n` or `N\n` and parse userspace boolean text.
- String helper copies the current string for read and replaces it with an RCU-published allocation on write.
- Blob helper reads/writes a fixed `debugfs_blob_wrapper`.
- u32 array helper formats a fixed array into an open-time buffer.
- regset32 helper reads hardware registers with optional runtime PM get/put.
- device-managed seqfile helper allocates a small devm-owned entry and opens a single seqfile.

## Important Dependencies

- `internal.h` for `debugfs_inode_info`, `debugfs_fsdata`, and method bit flags.
- VFS file operations, seq_file, simple_attr, simple_read/write helpers.
- Kernel lockdown API through `security_locked_down(LOCKDOWN_DEBUGFS)`.
- Module lifetime APIs through `fops_get()` and `fops_put()`.
- Runtime PM and I/O memory access for regset32 support.

## Edge Cases and Risks

- Unsafe debugfs file creators require callers to protect their handlers or use safe helper fops.
- Removal can block waiting for active users; cancellation callbacks exist to avoid deadlocks or long waits.
- Lockdown allows only strictly world-readable, non-mutating debugfs files without ioctl or mmap.
- String writes require strict append semantics and cap stored content to one page.
- Blob writes assume caller-provided storage remains valid and sized correctly.
