# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore.h

Read completely: 152 lines.

Defines Acorn FileCore on-disc structures and constants for kernel use. It describes boot block offsets, directory size and entry size, maximum directory entries, root inode sentinel, and the synthetic inode encoding where high bits contain a directory entry index and low bits contain a FileCore address.

`struct filecore_disc_record` models the boot/map disc record, including sector geometry, fragment id width, map layout, root directory address, disc size, name, type, and large-disc fields. Directory records are represented by `filecore_direntry`, `filecore_dirhead`, and `filecore_dirtail`.

The file also defines FileCore attribute bits for read/write/directory/owner access and macros to locate directory header, entries, and tail within the fixed 2048-byte directory block.
