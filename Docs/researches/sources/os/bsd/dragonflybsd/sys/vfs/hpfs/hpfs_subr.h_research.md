# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_subr.h

Source read: complete file, 83 lines.

Purpose: HPFS helper API header. It declares bitmap, codepage, file-size, update, lookup, creation/removal, typed-read, block-map, truncation, and extent-allocation helpers.

Key definitions:
- `hpfs_bmmarkfree()` and `hpfs_bmmarkbusy()` wrap `hpfs_bmmark()` with the correct bit state.
- `hpfs_u2d()`, `hpfs_d2u()`, and `hpfs_toupper()` implement byte conversion and case mapping through mount codepage tables.
- Macros `hpfs_breadalsec()` and `hpfs_breaddirblk()` specialize `hpfs_breadstruct()` for allocation sectors and directory blocks.

Integration:
- Included by HPFS implementation files after `hpfs.h`.
- Exposes cross-file dependencies between `hpfs_subr.c`, `hpfs_alsubr.c`, `hpfs_lookup.c`, `hpfs_vfsops.c`, and `hpfs_vnops.c`.

Risks and review notes:
- Conversion macros evaluate some arguments multiple times; callers should avoid side effects.
- The comment asks whether unsigned conversion is needed, signaling historical uncertainty around high-bit character handling.
