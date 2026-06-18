# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/iso.h

Read completely: 369 lines.

Purpose: defines ISO9660, Joliet, High Sierra, directory-record, extended-attribute, mount-state, filehandle, and endian conversion structures/macros used by the cd9660 filesystem.

Key definitions:
- `ISODCL()` models ISO fixed byte-position fields.
- `struct iso_volume_descriptor`, `iso_primary_descriptor`, `iso_supplementary_descriptor`, and `iso_sierra_primary_descriptor` describe volume descriptors.
- `struct iso_directory_record` represents variable-length directory entries; `ISO_DIRECTORY_RECORD_SIZE` is fixed at 33 because `sizeof` is unsafe for the trailing name field.
- `struct iso_extended_attributes` describes ISO extended attribute blocks.
- `enum ISO_FTYPE` identifies default ISO9660, plain 9660, RRIP, Joliet, ECMA, and High Sierra modes.
- `struct iso_mnt` is the in-kernel cd9660 mount state.
- `struct ifid` is the cd9660 filehandle payload.

Kernel-facing helpers:
- `VFSTOISOFS()`, `blkoff()`, `lblktosize()`, `lblkno()`, and `blksize()` wrap mount-state block math.
- Prototypes expose vnode, name conversion, directory inode, and rune helpers.

Endian helpers:
- `isonum_711`, `712`, `713`, `721`, `722`, `723`, `731`, `732`, and `733` decode ISO 7.x numeric encodings.
- Both-byte-order ISO fields currently return the little-endian half.

Research notes:
- The header is the contract between raw ISO media bytes and the rest of cd9660.
- `struct iso_mnt` includes GEOM consumer/bufobj pointers, root record copy, RRIP skip offsets, Joliet level, iconv handles, masks, uid/gid overrides, and block geometry.
