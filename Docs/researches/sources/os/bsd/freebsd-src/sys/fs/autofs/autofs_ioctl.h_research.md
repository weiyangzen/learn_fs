# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs_ioctl.h

## Purpose
Public ioctl ABI between the kernel autofs filesystem and `automountd`.

## Main Elements
- Defines `AUTOFS_PATH` as `/dev/autofs`.
- `struct autofs_daemon_request` carries request ID, map/from, full path, prefix, key, and mount options.
- `struct autofs_daemon_done_101` preserves compatibility with FreeBSD 10.1-era automountd completion format.
- `struct autofs_daemon_done` adds wildcard information and reserved spare fields.
- Defines `AUTOFSREQUEST`, `AUTOFSDONE101`, and `AUTOFSDONE` ioctl numbers.

## Dependencies And Integration
Included by kernel autofs and userland automount daemon code.

## Risk Notes
Field sizes are fixed at `MAXPATHLEN`; ABI compatibility is explicit for older daemon completion.
