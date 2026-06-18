# File Research: sources/virtualization/libguestfs/daemon/utils-c.c

## Role
Provides OCaml bindings for selected daemon utility functions.

## Exposed Bindings
- `guestfs_int_daemon_get_verbose_flag()`
- `guestfs_int_daemon_is_device_parameter()`
- `guestfs_int_daemon_is_root_device()`
- `guestfs_int_daemon_prog_exists()`
- `guestfs_int_daemon_udev_settle()`
- `guestfs_int_get_random_uuid()`

## Constraints
The file notes that OCaml-called utility bindings must not call daemon `reply*` functions. Most bindings are `[@@noalloc]`-style simple boolean wrappers.

## Filesystem/Storage Relevance
These bindings let OCaml daemon/inspection code reuse C-side device classification, tool probing, udev settling, and UUID generation.
