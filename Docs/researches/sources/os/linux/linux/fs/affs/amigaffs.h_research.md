# File Research: sources/os/linux/linux/fs/affs/amigaffs.h

Defines AFFS/Amiga on-disk constants and packed structures.

Key behavior:
- Defines filesystem type constants for OFS/FFS, international variants, directory-cache variants, and MUFS variants.
- Defines primary and secondary block type constants such as `T_SHORT`, `T_LIST`, `T_DATA`, `ST_FILE`, `ST_ROOT`, `ST_USERDIR`, `ST_SOFTLINK`, and link types.
- Defines root bitmap slot count and Amiga epoch delta.
- Defines Amiga date structures.
- Defines on-disk root block header and tail structures, including bitmap pointers, root/disk dates, disk name, and secondary type.
- Defines generic file/directory header and tail structures with hash table, uid/gid, protection, size, comment, date, name, link chain, hash chain, parent, extension, and secondary type.
- Defines symlink and data block layouts.
- Defines Amiga protection bit masks, including inverted classic owner flags and MUFS group/other flags.

Important interactions:
- Used by `affs.h` macros and AFFS implementation files to parse and modify on-disk blocks.
