# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/ufs_filio.h

## Role

Defines UFS-specific file ioctl data structures, logging ioctl result codes, and kernel ioctl helper prototypes.

## Key Structures

- `struct fioio` supports `_FIOIO`: input inode number and generation, output read-only file descriptor.
- `struct fioio32` is the ILP32-compatible form under `_SYSCALL32`.
- `struct fiotune` carries tunable superblock-style parameters: max contiguous allocation/directio size, rotational delay, max blocks per cylinder group, minfree, and optimization mode.
- `fiolog_t` returns logging enable/disable sizing and error status.

## Logging Errors

Defines `FIOLOG_ENONE`, `FIOLOG_ETRANS`, `FIOLOG_EROFS`, `FIOLOG_EULOCK`, `FIOLOG_EWLOCK`, `FIOLOG_ECLEAN`, and `FIOLOG_ENOULOCK`.

## Kernel Interfaces

Declares helpers for atime setting, direct I/O controls/query, inode-open ioctl, busy query, logging enable/disable/query, hole/data seek, and marking files compressed.

## Risk Notes

This header is part of UFS ioctl ABI. Structure layout and 32-bit compatibility fields must remain stable for user/kernel ioctl translation.
