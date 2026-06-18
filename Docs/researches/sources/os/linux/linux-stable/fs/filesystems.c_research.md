# File Research: sources/os/linux/linux-stable/fs/filesystems.c

This file maintains the global registry of filesystem types known to the kernel and exposes lookup, registration, module autoloading, `/proc/filesystems`, and the legacy `sysfs(2)` filesystem queries.

Major responsibilities:
- Register and unregister `struct file_system_type` instances.
- Validate filesystem parameter descriptions during registration.
- Maintain the linked list of filesystems under `file_systems_lock`.
- Manage module references for looked-up filesystem types.
- Implement `get_fs_type()` lookup with optional `request_module("fs-%s")`.
- Enforce subtype support for names containing a dot.
- List block-device-backed filesystem names for init-time consumers.
- Expose `/proc/filesystems` when procfs is enabled.
- Implement the historical `sysfs` syscall variants when configured.

Important design points:
- The registry is a simple linked list protected by an rwlock.
- `get_filesystem()` assumes the caller already owns a valid module reference and increments it.
- `__get_fs_type()` takes a module reference while still protected by the registry lock.
- Registering rejects duplicate names, names containing `.`, and already-linked filesystem types.
- Unregistering unlinks the filesystem and waits for an RCU grace period before returning.

Key invariants:
- Filesystem structures must not be freed until successfully unregistered.
- A filesystem can be inspected without the lock only after a module reference has been obtained.
- Subtyped names are accepted only when the base filesystem advertises `FS_HAS_SUBTYPE`.
- Module autoload success is not sufficient; the registry is checked again after `request_module()`.

External interfaces:
- Exports `register_filesystem`, `unregister_filesystem`, and `get_fs_type`.
- Provides `/proc/filesystems`, `list_bdev_fs_names()`, and optional `sysfs(2)`.
