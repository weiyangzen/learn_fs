# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/fsck.h

Defines shared structures, macros, state, and globals for `fsck_ffs`.

Important definitions:
- `union dinode` abstracts UFS1 and UFS2 inode layouts.
- `DIP` and `DIP_SET` read/write the active inode format.
- Per-inode states and `struct inostat` store allocation state, directory entry type, and unresolved link count.
- `inostathead` stores inode state arrays per cylinder group.
- Macros `GET_ISTATE`, `GET_ITYPE`, `SET_ISTATE`, `SET_ITYPE`, and `ILNCOUNT` access inode state.
- `bufarea` is the metadata buffer cache record, with UFS1/UFS2 indirect and inode views.
- `IBLK` and `IBLK_SET` abstract UFS1 32-bit vs UFS2 64-bit indirect block entries.
- `inodesc` is the common descriptor for inode block and directory scans.
- Duplicate block, zero-link inode, and directory inode cache structures mirror classic fsck design.

Global state includes:
- Superblock buffers and `sblock`.
- File descriptors, flags, clean/resolved status, and alternate superblock setting.
- Allocation bitmap, max block/inode, file/block counters.
- Lost+found name/mode.
- Info callback support.

This header is the central shared state contract for the FFS checker and handles the UFS1/UFS2 split.
