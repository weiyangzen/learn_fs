# File Research: sources/os/bsd/dragonflybsd/sys/vfs/isofs/cd9660/iso.h

## Scope

Defines ISO9660, High Sierra, Joliet, directory-record, extended-attribute, mount-state, and numeric conversion primitives for CD9660.

## Data Structures And APIs

- Defines `ISODCL()` for fixed byte-span declarations.
- Declares volume descriptor layouts: generic, primary ISO9660, supplementary/Joliet, and High Sierra primary.
- Defines descriptor type constants, standard IDs, and default 2048-byte block size.
- Defines `struct iso_directory_record` and `struct iso_extended_attributes`.
- Kernel section defines `enum ISO_FTYPE`, `struct iso_mnt`, block/offset macros, VFS init/vget declarations, name utilities, `isodirino()`, and `sgetrune()`.
- Inline `isonum_711` through `isonum_733` decode ISO 7.x numeric fields.
- Defines `ASSOCCHAR` for associated-file names.

## Dependencies

Used by nearly every CD9660 implementation file and by RRIP headers. Kernel-only pieces depend on mount, vnode, netexport, and CD9660 mount options.

## Risks And Invariants

On-disk numeric fields must be decoded through helper functions because ISO stores little, big, or both-endian encodings. `iso_mnt` centralizes mount mode, block geometry, Rock Ridge skip state, Joliet level, and iconv handles; inconsistent initialization would affect lookup, reads, and filehandle validation.
