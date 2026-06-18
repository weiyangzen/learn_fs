# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_extern.h

## Summary
Defines CD9660 kernel mount structure, filesystem type enum, block macros, global declarations, and filename conversion prototypes.

## Main Responsibilities
- Define sysctl value `CD9660_UTF8_JOLIET`.
- Define `enum ISO_FTYPE` for default, ISO 9660, Rock Ridge, and ECMA modes.
- Define `struct iso_mnt` with mount flags, Joliet level, device, owner/mask overrides, logical block geometry, root record metadata, type, and Rock Ridge skip values.
- Provide block offset/size macros.
- Declare VFS prototypes, node pool, Joliet UTF-8 tunable, vnode op vectors, `isodirino()`, and ISO filename conversion functions.

## Risks
This header is central to mount/node/lookup coupling. Block shift and mask fields must match the mounted image’s logical block size.
