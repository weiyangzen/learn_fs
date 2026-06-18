# File Research: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/ncheck_ffs.c

Purpose: Implements `ncheck_ffs`, a utility that scans an FFS/UFS filesystem image or raw device and prints pathnames for selected inodes.

Startup and device handling:
- `main()` parses `-a`, `-f format`, `-i inode...`, `-m`, and `-s`.
- Resolves device names through `opendev()`, `realpath()`, fstab lookup, and `rawname()`.
- Reads disk geometry through `DIOCGDINFO` and `DIOCGPDINFO`.
- Pledges `stdio` after opening the target.
- Searches standard superblock locations from `SBLOCKSEARCH` and accepts UFS1 or UFS2 superblocks.

Inode discovery:
- `findinodes()` iterates allocated inodes from `ROOTINO` to filesystem maximum.
- Directory inodes are cached so recursive path scanning can avoid rereads.
- If `-i` is used, only explicitly listed inodes are reported; otherwise all allocated inodes are candidates except when `-s` limits output to special/setuid style entries.
- `ilist` is dynamically grown by `addinode()` and sorted for binary search.

Inode/block I/O:
- `getino()` reads inode tables one cylinder group at a time and handles UFS1/UFS2 inode sizes through the `DIP()` macro.
- `bread()` reads disk blocks with error recovery: on a failed large read, it zeroes the buffer and retries sector-by-sector, stopping after `BREADEMAX` errors.
- Reads are done with `pread()` using DEV_BSIZE-based block offsets.

Directory traversal:
- `scanonedir()` walks direct and indirect directory blocks for a cached directory inode.
- `dirindir()` recursively follows indirect blocks for directory data.
- `searchdir()` parses `struct direct` entries, skips `.` and `..` unless `-a`, prints matches, and recursively descends into subdirectories.

Output:
- Default output is `inode path`, with optional `-m` mode/uid/gid prefix.
- Directory matches are printed with `/.` suffix.
- `-f format` enables `format_entry()`, supporting escapes such as `\I` for inode and `\P` for path plus common C-style escapes.

Risk/edge notes:
- The scanner trusts on-disk directory record lengths except for a zero-length corruption guard.
- Traversal is recursive by discovered directory structure and depends on cached directory inode metadata.
