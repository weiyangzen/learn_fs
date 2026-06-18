# File Research: sources/os/bsd/dragonflybsd/sys/sys/xdiskioctl.h

## Summary
Minimal ioctl ABI for xdisk attach/detach.

## Main Responsibilities
- Defines `struct xdisk_attach_ioctl` with file descriptor and reserved fields.
- Defines `XDISKIOCATTACH` and `XDISKIOCDETACH`.

## Important Behavior
The reserved array leaves room for ABI extension without changing the ioctl payload size immediately.

## Risks
The attach API passes a raw file descriptor, so kernel-side implementation must validate descriptor type, lifetime, and permissions.
