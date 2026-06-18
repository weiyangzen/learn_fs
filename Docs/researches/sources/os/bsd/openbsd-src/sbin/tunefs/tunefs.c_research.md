# File Research: sources/os/bsd/openbsd-src/sbin/tunefs/tunefs.c

UFS/FFS filesystem superblock tuning utility.

Options:
- `-A`: update all superblock copies.
- `-F`: treat argument as direct file/device path instead of resolving partition.
- `-N`: print current settings and make no changes.
- `-e maxbpg`: max blocks per file in a cylinder group.
- `-g avgfilesize`: average file size.
- `-h avgfpdir`: expected files per directory.
- `-m minfree`: minimum free percentage.
- `-o space|time`: optimization preference.

Implementation:
- Opens filesystem read-only for `-N`, read-write otherwise.
- Resolves mount path to raw device via `getfsfile()` and `opendev()` unless `-F`.
- Pledges `stdio` after opening the target.
- `getsb()` searches known superblock locations from `SBLOCKSEARCH`, accepts UFS1/UFS2 magic, respects UFS2 location and updated flags.
- Updates selected fields in `struct fs`, warning on changes/no-ops and minfree/optimization mismatches.
- Writes primary superblock and optionally all cylinder group superblock copies.
- `bread()`/`bwrite()` use `pread()`/`pwrite()` at block offsets.

Filesystem/storage relevance:
- Direct local filesystem metadata editor for FFS/UFS superblocks. It is highly relevant to filesystem layout/tuning research and shows OpenBSD’s expected mutable superblock parameters.
