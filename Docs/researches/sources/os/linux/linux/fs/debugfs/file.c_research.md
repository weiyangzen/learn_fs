# File Research: sources/os/linux/linux/fs/debugfs/file.c

## Role

Implements debugfs file operation helpers, proxy file operations, removal-safety tracking, cancellation support, lockdown checks, and common typed debugfs file constructors.

## Major Responsibilities

- Provides safe wrappers around debugfs file operations so removal waits for active users.
- Supports unsafe file creation where callers handle `debugfs_file_get()` / `debugfs_file_put()` themselves.
- Implements cancellation hooks for long-running debugfs operations during removal.
- Enforces lockdown restrictions for sensitive debugfs files.
- Provides helper constructors for scalar values, booleans, strings, blobs, arrays, register sets, and device-managed seq files.

## Active-User Lifetime Model

The key structure is `struct debugfs_fsdata`, attached to `dentry->d_fsdata`.

`__debugfs_file_get()` lazily allocates this state and records:

- Real full `file_operations`, or short debugfs operations.
- Available method bits: read, write, llseek, poll, ioctl.
- `active_users` refcount.
- Completion used by removal waiters.
- Cancellation list and mutex.

`debugfs_file_get()` marks the beginning of safe file-data access. It returns `-EIO` when the file was already removed.

`debugfs_file_put()` drops active-user state and completes removal waiters when the last user leaves.

## Cancellation Support

`debugfs_enter_cancellation()` registers a stack-owned cancellation object while a debugfs operation is active.

`debugfs_leave_cancellation()` removes it.

During removal, `debugfs/inode.c` can invoke registered `cancel()` callbacks so operations waiting on hardware or async work can break out instead of causing removal deadlock.

## Lockdown Behavior

`debugfs_locked_down()` permits only world-readable, non-writing, non-mutating files while kernel lockdown applies. Files with write mode, write-open, ioctl, compat ioctl, or mmap paths are blocked via `security_locked_down(LOCKDOWN_DEBUGFS)`.

This is used by proxy open paths before handing control to real file operations.

## Proxy File Operations

The file defines multiple proxy layers:

- `debugfs_open_proxy_file_operations`: protects only open, then replaces fops with real fops.
- `debugfs_full_proxy_file_operations`: protects open/read/write/llseek/poll/ioctl/release through debugfs active-user tracking.
- `debugfs_full_short_proxy_file_operations`: supports `debugfs_short_fops`.

Macro-generated proxy functions call `debugfs_file_get()`, dispatch to the underlying operation if supported, and call `debugfs_file_put()`.

`full_proxy_release()` deliberately calls real release unconditionally because release must clean up resources even after debugfs removal.

## Attribute Helpers

Exports protected simple-attribute wrappers:

- `debugfs_attr_read()`
- `debugfs_attr_write()`
- `debugfs_attr_write_signed()`

Typed constructors include:

- Unsigned decimal:
  - `debugfs_create_u8()`
  - `debugfs_create_u16()`
  - `debugfs_create_u32()`
  - `debugfs_create_u64()`
  - `debugfs_create_ulong()`
  - `debugfs_create_size_t()`
- Hex:
  - `debugfs_create_x8()`
  - `debugfs_create_x16()`
  - `debugfs_create_x32()`
  - `debugfs_create_x64()`
- Signed atomic:
  - `debugfs_create_atomic_t()`
- Boolean:
  - `debugfs_create_bool()`
- String:
  - `debugfs_create_str()`
- Blob:
  - `debugfs_create_blob()`
- U32 array:
  - `debugfs_create_u32_array()`

`debugfs_create_mode_unsafe()` chooses read-only, write-only, or read/write fops based on mode bits.

## String Handling

`debugfs_read_file_str()` snapshots the string under debugfs active-user protection and returns a newline-terminated copy.

`debugfs_write_file_str()` allows strict concatenation only, limits strings to one page, replaces the pointed-to string with RCU assignment, synchronizes RCU, and frees the old string.

Callers must provide a non-NULL `char **` and non-NULL initial string.

## Blob and Array Handling

`debugfs_create_blob()` exposes caller-provided binary memory through `simple_read_from_buffer()` and `simple_write_to_buffer()`.

`debugfs_create_u32_array()` formats a fixed-size u32 array into a per-open buffer; writes and seeking are unsupported.

## Register and Device Helpers

Under `CONFIG_HAS_IOMEM`:

- `debugfs_print_regs32()` prints named 32-bit registers.
- `debugfs_create_regset32()` creates a seq-file register dump and uses runtime PM get/put when a device is attached.

`debugfs_create_devm_seqfile()` allocates a debugfs seq-file entry with device-managed memory.

## Important Invariants

- Active-user protection is dentry-based and depends on `dentry->d_fsdata`.
- Removal may wait for active users; long operations should use cancellation.
- Unsafe files must use explicit `debugfs_file_get()` / `debugfs_file_put()` in their handlers.
- Lockdown filtering is based partly on file mode and operation availability.
- Real fops ownership is acquired with `fops_get()` and released with `fops_put()`.

## Research Notes

This file is less about storage and more about lifetime safety for debug instrumentation. The critical design point is that debugfs files often expose module or driver-owned memory, so removal synchronization is the main correctness concern.
