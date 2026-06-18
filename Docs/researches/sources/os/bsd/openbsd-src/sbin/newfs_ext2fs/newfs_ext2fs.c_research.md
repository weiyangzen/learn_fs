# File Research: sources/os/bsd/openbsd-src/sbin/newfs_ext2fs/newfs_ext2fs.c

Purpose: Front-end for creating ext2 filesystems. It parses options, opens devices or image files, derives geometry and defaults, checks mounted-device safety, and calls `mke2fs()`.

CLI behavior:
- Supports dry run `-N`, image-file mode `-F`, force partition-type ignore `-I`, zero/preallocate image `-Z`, inode size `-D`, format revision `-O`, sector size `-S`, verbosity `-V`/`-q`, block/fragment size, density, minfree, explicit inode count, size, volume name, and compatibility `-t`.
- Uses `strsuftoi64()` for numeric options with `k/m/g/b` byte suffix support and `s` sector suffix behavior.

Device/image handling:
- Image mode opens a regular target, can create/truncate it, and uses default 512-byte sectors unless overridden.
- Device mode uses `opendev()`, refuses mounted targets unless dry-run, reads disklabel, and requires `FS_EXT2FS` partition type unless `-I`.
- Size comes from explicit `-s`, regular file size, or partition size.

Defaults:
- Filesystems below 4 MB use 1 KB blocks and fewer default inodes.
- Filesystems below 512 MB also default to 1 KB blocks.
- Larger filesystems default to 4 KB blocks.
- Default inode count scales by blocks per inode density tiers unless overridden by `-i` or `-n`.

Safety/privilege:
- Pledges `stdio rpath wpath cpath disklabel`.
- Mounted target detection mirrors other OpenBSD newfs utilities by normalizing `/dev` raw/character names.

Support routines:
- `getdisklabel()` reads `DIOCGDINFO`, with unused disktype fallback retained.
- `getpartition()` validates character device expectations and resolves partition by trailing device name.
