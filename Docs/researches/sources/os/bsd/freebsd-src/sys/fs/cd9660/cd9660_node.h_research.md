# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.h

## Purpose
Defines cd9660 in-memory node structures and vnode-operation prototypes.

## Main Elements
- Defines `doff_t` for directory offsets.
- `ISO_RRIP_INODE` stores POSIX-like attributes: times, mode, uid, gid, link count, and device number.
- `struct iso_node` stores vnode, inode number, mount pointer, lockf head, lookup offsets, extent, size, data start, and attributes.
- Defines `VTOI()` and `ITOV()` conversion macros.
- Declares malloc types and cd9660 lookup, inactive, reclaim, bmap, block-at-offset, default attribute, and timestamp functions.

## Dependencies And Integration
Included by cd9660 vnode, lookup, node, and bmap code.

## Risk Notes
`iso_node` encodes the relationship between ISO directory records, file extents, and VFS vnode identity.
