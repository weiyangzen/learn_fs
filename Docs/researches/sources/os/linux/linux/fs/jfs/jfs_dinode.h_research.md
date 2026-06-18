# File Research: sources/os/linux/linux/fs/jfs/jfs_dinode.h

## Purpose
Defines the 512-byte on-disk JFS inode layout and extended inode mode/attribute flags.

## Main Structures
- `struct dinode` contains the base 128-byte POSIX/generic area: inode stamp, fileset, number, generation, inode extent descriptor, size, block count, nlink, uid/gid, mode, timestamps, ACL/EA descriptors, directory index state, and ACL type.
- The trailing 384 bytes are a union:
  - Directory form stores a 12-entry inline directory index table and a dtree root.
  - File/special form stores imap generator data, xtree root or special-file data, device id, fast symlink storage, inline EA storage, and combined inline storage.
- Macros alias union fields such as `di_dtroot`, `di_parent`, `di_xtroot`, `di_rdev`, `di_fastsymlink`, and `di_inlineea`.

## Constants and Flags
- `INODESLOTSIZE`, `L2INODESLOTSIZE`, and `log2INODESIZE` describe inode sizing.
- Extended mode bits include journaled file, sparse, inline-EA-free, swapfile, OS/2-style readonly/hidden/system/archive/name flags, and directory shadow bit.
- Linux-visible JFS flags include noatime, dirsync, sync, secure deletion, undelete, append, immutable.
- `JFS_FL_USER_VISIBLE`, `JFS_FL_USER_MODIFIABLE`, and `JFS_FL_INHERIT` define fileattr masks.

## Dependencies
- Uses on-disk descriptor types (`pxd_t`, `dxd_t`, `dtroot_t`, `xtroot_t`, `timestruc_t`) from other JFS headers.

## Notable Details
- Comments preserve OS/2 JFS layout compatibility and explain why the inode was not redesigned despite awkward union overlays.
- Fast symlink storage is expected to overflow into inline EA space when needed, clearing the `INLINEEA` flag.
