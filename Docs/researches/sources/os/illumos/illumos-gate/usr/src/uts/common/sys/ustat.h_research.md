# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ustat.h

## Role

Defines the obsolete SVR4 `ustat` filesystem statistics structure.

## Key Interfaces

- Emits a compile-time error for non-LP64 large-file compilation environments because `ustat` is incompatible there.
- `struct ustat` contains free-block count, free-inode count, filesystem name, and filesystem pack name.
- `_SYSCALL32` defines `struct ustat32` with 32-bit block and inode fields.

## Design Notes

The header warns applications to migrate to `statvfs(2)`.

## Risk Notes

This is legacy ABI. Structure sizes and large-file restrictions must remain compatible with old binaries and syscall32 translation.
