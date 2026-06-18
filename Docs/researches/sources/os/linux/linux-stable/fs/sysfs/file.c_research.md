# File Research: sources/os/linux/linux-stable/fs/sysfs/file.c

Purpose: Implements sysfs regular and binary attribute files using kernfs callbacks.

Key responsibilities:
- Maps kernfs nodes back to kobjects and their `sysfs_ops`.
- Implements text attribute show/store callbacks through seq_file or preallocated buffers.
- Implements binary attribute read, write, mmap, llseek, and open callbacks.
- Selects kernfs operation tables based on readable/writable/preallocated/binary/mmap capabilities.
- Creates and removes individual attributes, arrays of attributes, group members, and binary attributes.
- Implements `sysfs_notify()` for poll notification.
- Provides active-protection break/unbreak helpers for self-removing attributes.
- Implements chmod and ownership changes for files, symlinks, and kobject default groups.
- Provides `sysfs_emit()`, `sysfs_emit_at()`, and `sysfs_bin_attr_simple_read()` helpers.

Important interactions:
- Depends on kobject `ktype->sysfs_ops`.
- Uses kernfs for active references, file creation, notification, ownership, and removal.
- Coordinates ownership changes with group helpers from `group.c`.

Notable invariants and risks:
- Text `show()` buffers are page-sized; returning `PAGE_SIZE` or more is treated as suspicious and truncated.
- Preallocated text reads require the kernfs prealloc buffer.
- `sysfs_break_active_protection()` deliberately weakens deletion protection and must be paired with `sysfs_unbreak_active_protection()`.
