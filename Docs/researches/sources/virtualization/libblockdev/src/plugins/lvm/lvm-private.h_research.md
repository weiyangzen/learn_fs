# File Research: sources/virtualization/libblockdev/src/plugins/lvm/lvm-private.h

## Purpose

`lvm-private.h` defines private constants and shared globals for libblockdev's LVM plugin implementations.

## Constants

- `SECTOR_SIZE` is fixed at 512 bytes.
- `DEFAULT_PE_SIZE` is 4 MiB.
- `USE_DEFAULT_PE_SIZE` is 0.
- `RESOLVE_PE_SIZE(size)` maps `0` to `DEFAULT_PE_SIZE`; otherwise it preserves the caller-supplied size.
- `LVM_MIN_VERSION` is `2.03.17`.
- `LVM_VERSION_FSRESIZE` is `2.03.19`.

## Shared Globals

The header declares:

- `global_config_lock`
- `global_config_str`
- `global_devices_str`

These are defined in `lvm-common.c` and used by both backend implementations to inject process-local LVM configuration and device filters into command or D-Bus operations.

## Research Notes

This is a small private coordination header. Its main impact is ensuring consistent byte-sector assumptions, default PE sizing, minimum LVM version checks, and shared config/device-filter handling across LVM backends.
