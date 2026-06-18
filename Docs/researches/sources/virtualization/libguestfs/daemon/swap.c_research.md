# File Research: sources/virtualization/libguestfs/daemon/swap.c

## Role
Implements daemon actions for creating, enabling, disabling, and relabeling Linux swap devices and swap files.

## Main Operations
- `do_mkswap()` wraps `mkswap -f`, with optional `-L` label and `-U` UUID.
- `do_mkswap_L()` and `do_mkswap_U()` are compatibility wrappers that set `optargs_bitmask`.
- `do_mkswap_file()` maps a guest path through `sysroot_path()` and runs `mkswap` on the file.
- `do_swapon_*()` and `do_swapoff_*()` wrap `swapon` and `swapoff` for devices, files, labels, and UUIDs.
- `swap_set_uuid()` and `swap_set_label()` wrap `swaplabel`.

## Validation and Side Effects
- Swap labels are limited to 16 bytes.
- Device creation calls `wipe_device_before_mkfs()` before `mkswap`.
- Swap on/off operations call `udev_settle()` after command completion.

## Filesystem/Storage Relevance
This file manages swap signatures and active swap state on guest block devices/files, including UUID/label metadata used by `/etc/fstab` and boot-time activation.
