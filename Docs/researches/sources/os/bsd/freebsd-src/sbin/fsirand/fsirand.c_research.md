# File Research: sources/os/bsd/freebsd-src/sbin/fsirand/fsirand.c

## Purpose

Randomizes UFS inode generation numbers and filesystem IDs, or prints existing generation numbers in print-only mode.

## Main Entry Points

- `main(int argc, char *argv[])`
- `fsirand(char *device)`

## Options

- `-b`: accepted as `ignorelabel`, but not otherwise used in this file.
- `-f`: force operation past one clean-state check.
- `-p`: print generation numbers instead of modifying.

## Operation

1. Opens the device read-only for print mode or read-write for modification.
2. Reads the superblock with `sbget()`.
3. Rejects unclean filesystems or old UFS1 inode formats.
4. Allocates one cylinder group’s worth of inode buffer.
5. In modification mode:
   - Updates `fs_id[0]` with current time and `fs_id[1]` with `arc4random()`.
   - Writes superblock and backups with `sbput()`.
   - Iterates each cylinder group, reads inode blocks, assigns random `di_gen` values, updates UFS2 dinode checksums, and writes the inode buffer back.
6. In print mode:
   - Prints fsid information if present.
   - Prints each inode number and generation.

## Integration Points

Uses libufs superblock functions and UFS/FFS macros such as `fsbtodb()`, `ino_to_fsba()`, `UFS_ROOTINO`, and `ffs_update_dinode_ckhash()`.

## Risk Notes

Requires a clean filesystem unless forced for a secondary clean-state check. It rewrites large inode regions directly and updates UFS2 dinode checksums, so interrupted writes can require fsck.
