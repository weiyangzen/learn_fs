# File Research: sources/os/linux/linux/fs/xfs/xfs_sysctl.h

## Purpose

`xfs_sysctl.h` defines the storage structures, sysctl IDs, globals, and conditional registration interface for XFS tunables.

## Main Interfaces

- `xfs_sysctl_val_t`: min/current/max triple for integer sysctl values.
- `xfs_param_t`: grouped XFS tunables backing the sysctl table.
- Sysctl ID enum: legacy numeric IDs for XFS sysctl options, with gaps for removed or disabled tunables.
- `struct xfs_globals`: global debug and runtime knobs not represented as `xfs_param_t`.
- `xfs_params`: external instance of `xfs_param_t`.
- `xfs_globals`: external instance of `struct xfs_globals`.
- `xfs_sysctl_register` / `xfs_sysctl_unregister`: real declarations under `CONFIG_SYSCTL`, no-op macros otherwise.

## Tunable Coverage

- Error reporting and panic behavior.
- Sync and blockgc timers.
- Stats clearing.
- Inheritance of sync, nodump, noatime, nosymlinks, and nodefrag inode flags.
- inode32 rotor step.
- Filestream timeout.
- Debug-only parallel workqueue threads and logged attribute recovery persistence.
- Bulk load slack controls, log recovery delay, mount delay, fatal assert behavior, and always-COW testing.

## Implementation Notes

- Comments describe `error_level` values and the interaction with `xfs_panic_mask`.
- Some enum IDs are preserved as comments for removed historical sysctls, which helps maintain ABI/context for old numeric identifiers.
- Debug-only fields in `struct xfs_globals` are protected by `#ifdef DEBUG`; non-debug fields remain available for production builds.

## Dependencies and Callers

- Included by code that defines or uses global tunables, including `xfs_sysctl.c`, `xfs_sysfs.c`, and `xfs_super.c`.
- `xfs_sysfs.c` exposes many `xfs_globals` fields under debug sysfs.

## Research Notes

- This file separates tunables backed by sysctl min/val/max triples from broader globals exposed through debug sysfs or used internally.
