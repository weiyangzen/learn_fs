# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/cd9660_node.h

## Scope

Defines the CD9660 in-memory inode structure and public vnode/node helper interfaces used by the ISO9660 implementation.

## APIs And Data Structures

- Defines `doff_t` as `long` for directory offsets.
- `ISO_RRIP_INODE` stores POSIX-like metadata synthesized from ISO/Rock Ridge records: access, modification, change times, mode, UID, GID, link count, and device number.
- `struct iso_node` stores hash linkage, vnode/device vnode pointers, device identity, pseudo-inode number, mount pointer, byte-range lock state, directory lookup cache offsets, ISO extent/start/size fields, and embedded `ISO_RRIP_INODE`.
- `VTOI()` and `ITOV()` convert between vnode and ISO node.
- Declares malloc types `M_ISOFSMNT` and `M_ISOFSNODE`.
- Declares vnode operation helpers including lookup, inactive, reclaim, bmap, block-offset reads, default attribute/timestamp extraction, inode hash access, and timestamp conversion.

## Dependencies

Requires vnode, device, lockf, buffer, ISO directory-record, mount, and VOP argument types supplied by the kernel and adjacent CD9660 headers.

## Risks And Invariants

`i_number` is not an on-disk inode number in the Unix sense; it is derived from ISO directory record location or extent. Directory offset fields are tuned for practical CD sizes rather than theoretical multi-gigabyte directories.
