# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_superblock.h

## Role

Defines the on-disk JFS superblock layout and declares mount, unmount, superblock, and extendfs interfaces.

## Key Definitions

- `JFS_MAGIC` is `"JFS1"`.
- `JFS_VERSION` is `2`.
- `LV_NAME_SIZE` and `LV_LABEL_SIZE` preserve OS/2 layout expectations.
- `struct jfs_superblock` stores magic, version, aggregate size, block sizes, allocation group size, flags, state, compression fields, root inode number, DASD fields, log descriptor/device/serial/UUID, fsck workspace, timestamps, filesystem UUID/label/log label, and secondary AIM/AIT descriptors.

## Public Interfaces

Declares:
`readSuper`, `updateSuper`, `jfs_error`, `jfs_mount`, `jfs_mount_rw`, `jfs_umount`, `jfs_umount_rw`, `jfs_extendfs`, `jfsIOthread`, and `jfsSyncThread`.

## Design Notes

This header is the shared contract between mount, unmount, log setup, and filesystem growth code. Endianness is explicit in all on-disk fields.
