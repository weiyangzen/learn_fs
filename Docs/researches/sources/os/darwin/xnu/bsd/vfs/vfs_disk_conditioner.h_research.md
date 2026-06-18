# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_disk_conditioner.h

## Scope

This private VFS header declares the disk conditioner kernel-private API.

## APIs And Constants

- Declares `disk_conditioner_get_info(mount_t, disk_conditioner_info *)`.
- Declares `disk_conditioner_set_info(mount_t, disk_conditioner_info *)`.
- Declares `disk_conditioner_mount_is_ssd(mount_t)`.

## Dependencies And Role

The declarations are exposed only under `KERNEL_PRIVATE` and depend on `sys/fsctl.h` for `disk_conditioner_info`.

## Risks And Invariants

- The header intentionally does not expose `disk_conditioner_delay()` or unmount cleanup; those are internal call-site contracts.
- Consumers must compile with kernel-private mount and fsctl definitions available.
