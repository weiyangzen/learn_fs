# File Research: sources/os/linux/linux/fs/filesystems.c

Read status: complete, 413 lines.

Purpose: maintains the kernel registry of filesystem types and exposes lookup/listing interfaces.

Key flow:
- `register_filesystem()` validates parser descriptions, rejects duplicate names, links a `file_system_type` into an RCU hlist, and invalidates the cached `/proc/filesystems` string.
- `unregister_filesystem()` removes from the RCU hlist and waits for readers with `synchronize_rcu()`.
- Optional `sysfs(2)` compatibility handlers return filesystem index/name/count.
- `list_bdev_fs_names()` emits registered block-device-backed filesystem names for early boot use.
- `/proc/filesystems` uses a generation-stamped cached string, regenerated lazily and invalidated on registry changes.
- `get_fs_type()` looks up a type, requests `fs-<name>` module autoload on miss, and enforces subtype support after a dot suffix.

Important dependencies: module references, RCU hlist traversal, procfs seq output, kmod autoloading, filesystem parser validation.

Risk/concurrency notes:
- Readers must take module references before using an fs type after leaving RCU.
- Cached proc output is intentionally best-effort; allocation failure falls back to direct seq iteration.
