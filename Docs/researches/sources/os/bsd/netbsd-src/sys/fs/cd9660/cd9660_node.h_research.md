# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.h

## Summary
Defines CD9660 vnode-private node structures, Rock Ridge inode metadata, flags, conversion macros, and vnode operation prototypes.

## Main Responsibilities
- Define `doff_t` as directory offset type.
- Define `ISO_RRIP_INODE` with timestamps, mode, uid/gid, link count, and special-device id.
- Define `struct iso_node` embedding `genfs_node`, vnode/device references, inode identity, mount pointer, directory lookup caches, extent/start/size, and derived inode attributes.
- Define `VTOI()` and `ITOV()` conversions.
- Declare CD9660 vnode operation functions and helpers.

## Risks
`doff_t` is `long`, with comments noting large directories may exceed 2 GB in theory. The structure’s directory offset cache is tightly coupled to lookup behavior.
