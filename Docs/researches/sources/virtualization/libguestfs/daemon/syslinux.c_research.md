# File Research: sources/virtualization/libguestfs/daemon/syslinux.c

## Role
Implements daemon actions for installing Syslinux and Extlinux bootloaders.

## Main Operations
- `optgroup_syslinux_available()` and `optgroup_extlinux_available()` probe for `syslinux` and `extlinux`.
- `do_syslinux()` runs `syslinux --install --force`, optionally with `--directory`.
- `do_extlinux()` maps the guest directory through `sysroot_path()` and runs `extlinux --install`.

## Error Handling
External command stderr is captured and returned through `reply_with_error`.

## Filesystem/Storage Relevance
This file supports bootloader installation into guest filesystems or devices, a common operation after manipulating boot partitions or disk images.
