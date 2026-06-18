# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_mount.c

## Role

Implements JFS aggregate/fileset mount setup, read-write mount completion, superblock validation/update, raw superblock read, and mount log record emission.

## Main Responsibilities

- `jfs_mount()` validates the superblock, opens and mounts the aggregate inode allocation map, aggregate block map, optional secondary aggregate inode map, and fileset inode allocation map.
- Error paths unwind mounted maps and special inodes in reverse order.
- `jfs_mount_rw()` handles read-write mount or remount:
  - Revalidates clean state on remount.
  - Truncates cached inode/block map pages.
  - Remounts imap/bmap.
  - Opens the journal through `lmLogOpen()`.
  - Updates the superblock to `FM_MOUNT`.
  - Writes a `LOG_MOUNT` record.
- `chkSuper()` reads the superblock, validates magic/version, enforces 4 KiB block size, rejects dirty read-write mounts, validates secondary AIM/AIT descriptors, enables group commit flag, and copies mount parameters into `jfs_sb_info`.
- `updateSuper()` writes filesystem state transitions and records log device/serial on mount.
- `readSuper()` tries primary superblock first, then replicated secondary.
- `logMOUNT()` writes a mount record to stop replay from crossing this mount boundary for the aggregate.

## Important Interactions

- Uses `diReadSpecial`, `diMount`, `diUnmount`, and `diFreeSpecial` for internal inode maps.
- Uses `dbMount` and `dbUnmount` for the aggregate block map.
- Uses `lmLogOpen`, `lmLogClose`, and `lmLog` from the log manager.
- Populates `sbi->logpxd`, `logdev`, `loguuid`, `fsckpxd`, `ait2`, `uuid`, and block-size derived fields.

## Correctness Notes

- JFS Linux mount path only supports `PSIZE` 4 KiB filesystem block size.
- Dirty filesystems are rejected for read-write mount.
- No-integrity mounts alter `updateSuper()` state handling to preserve the prior state while presenting dirty semantics internally.
