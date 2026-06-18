# File Research: sources/local-fs/e2fsprogs/misc/dumpe2fs.8.in

## Purpose
Manual page template for `dumpe2fs`, the ext2/ext3/ext4 superblock and block group information dumper.

## Documented Interface
- Synopsis: `dumpe2fs [-bfghixV] [-o superblock=num] [-o blocksize=num] device`
- Device can be a path, `LABEL=...`, or `UUID=...`.
- Options:
  - `-b`: print reserved bad blocks.
  - `-o superblock=...`: use an alternate superblock.
  - `-o blocksize=...`: force a block size.
  - `-f`: force display despite unknown features.
  - `-g`: machine-readable group descriptor format.
  - `-h`: superblock only.
  - `-i`: read an `e2image` image file.
  - `-m`: MMP safety/status checking.
  - `-x`: hexadecimal block numbers.
  - `-V`: version output.

## Important Notes
- Warns that output from mounted filesystems may be stale or inconsistent.
- Documents exit codes as nonzero for errors, checksum problems, invalid superblocks, or unsafe MMP state.
- References `e2mmpstatus`, `e2fsck`, `mke2fs`, `tune2fs`, and `ext4`.
