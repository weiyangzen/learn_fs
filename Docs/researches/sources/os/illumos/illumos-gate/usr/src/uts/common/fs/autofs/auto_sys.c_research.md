# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/autofs/auto_sys.c

## Purpose

`auto_sys.c` implements the `autofssys()` syscall dispatcher used by autofs userland, mainly for registering the automountd door handle and forcing cleanup of a zone's autofs mounts.

## File Shape

- Size: 101 lines, 2,816 bytes.
- SHA-256: `19bfaf365e061e30db3857fc7f765c7ee2305b57c9af451ee2709cd8400557f7`.
- Single entry point: `autofssys(enum autofssys_op opcode, uintptr_t arg)`.

## Core Behavior

- `AUTOFS_UNMOUNTALL` is restricted to callers with filesystem unmount privilege in the global zone. It looks up the target zone by ID, fetches its autofs globals, and calls `unmount_tree(fngp, B_TRUE)` for forced in-kernel cleanup. Absence of autofs globals is treated as success because there are no mounts to clean.
- `AUTOFS_SETDOOR` initializes current-zone autofs globals if needed, copies in a door ID, replaces any existing door handle, stores the new `door_ki_lookup()` result, and records the automountd process ID.
- Unknown opcodes return `EINVAL`; copy failures return `EFAULT`; authorization failures return `EPERM`.

## Dependencies And Contracts

- Uses `autofs_minor_lock` to serialize zone-specific global initialization and door handle replacement.
- Relies on `autofs_zone_init()` from `auto_vfsops.c` and `unmount_tree()` from `auto_subr.c`.
- Uses zone-specific data key `autofs_key`.

## Maintenance Notes

This syscall is a small but important control boundary. `AUTOFS_UNMOUNTALL` deliberately allows the global zone to clean another zone's autofs state during shutdown, while `AUTOFS_SETDOOR` is per-current-zone and creates the daemon communication endpoint used by the rest of autofs.
