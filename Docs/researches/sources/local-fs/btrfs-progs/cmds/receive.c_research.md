# File Research: sources/local-fs/btrfs-progs/cmds/receive.c

## Purpose

Implements `btrfs receive`, including normal send-stream replay and `--dump` mode. It applies Btrfs send-stream operations to a destination filesystem, creates subvolumes/snapshots, writes data, clones extents, restores metadata, and finalizes received subvolumes.

## Main Context

`struct btrfs_receive` stores:

- mount and destination directory fds
- cached write fd/path
- root and destination path state
- current subvolume metadata
- chroot/end-command behavior
- forced decompression flag
- reusable zlib/zstd decompression state

## Command Options

- `-f FILE`: read stream from file instead of stdin.
- `-e`: honor end-command marker.
- `-C, --chroot`: chroot to destination.
- `-E, --max-errors`: maximum stream command errors.
- `-m ROOTMOUNT`: explicit root mount point.
- `--force-decompress`: always decompress encoded writes rather than using encoded I/O.
- `--dump`: print stream operations instead of replaying.
- `-q`, `-v`: quiet/verbose controls.

## Send-Stream Replay Operations

The `send_ops` callback table implements:

- subvolume and snapshot creation
- file, directory, fifo, socket, node, and symlink creation
- rename, hardlink, unlink, rmdir
- write and clone
- xattr set/remove
- truncate, chmod, chown, utimes
- update_extent no-op for no-file-data sends
- encoded_write with direct encoded I/O or decompression fallback
- fallocate
- fileattr no-op placeholder
- fs-verity enable when compiled with fsverity headers

## Key Helpers

- `finish_subvol()` sets received subvolume metadata with `BTRFS_IOC_SET_RECEIVED_SUBVOL` and makes the subvolume read-only.
- `process_subvol()` creates a new received subvolume and records received UUID/transid.
- `search_source_subvol()` finds source subvolumes by received UUID first, then regular UUID.
- `process_snapshot()` resolves parent subvolume, adjusts paths relative to the active root, and creates a snapshot with `BTRFS_IOC_SNAP_CREATE_V2`.
- `open_inode_for_write()` caches the current writable file fd across write-like operations.
- `process_clone()` resolves clone source subvolume/path and uses `BTRFS_IOC_CLONE_RANGE`.
- `process_encoded_write()` tries `BTRFS_IOC_ENCODED_WRITE`, falling back to userspace decompression for selected errors.
- `decompress_zlib()`, `decompress_zstd()`, and `decompress_lzo()` implement decompression backends when compiled in.
- `do_receive()` resolves destination/root mount context, optionally chroots, processes one or more streams, and finalizes subvolumes after each stream.

## Important Behavior

- Received subvolumes are made read-only immediately after stream completion.
- Snapshot parent lookup accepts both received UUID and normal UUID, improving compatibility with incremental streams.
- If receiving under a non-root mounted subvolume, source paths are adjusted so clone/snapshot sources remain reachable from the current mount context.
- Empty streams are rejected.
- `--dump` bypasses filesystem writes and delegates to `btrfs_print_send_ops`.
- `fileattr` is currently ignored because Btrfs inode flags cannot be directly applied as Linux `FS_IOC_SETFLAGS` flags without conversion and special handling.
- fs-verity support is compile-time dependent.

## External Interfaces

Uses Btrfs ioctls:

- `BTRFS_IOC_SET_RECEIVED_SUBVOL`
- `BTRFS_IOC_SUBVOL_GETFLAGS`
- `BTRFS_IOC_SUBVOL_SETFLAGS`
- `BTRFS_IOC_SUBVOL_CREATE`
- `BTRFS_IOC_SNAP_CREATE_V2`
- `BTRFS_IOC_CLONE_RANGE`
- `BTRFS_IOC_ENCODED_WRITE`

Also uses xattr syscalls, filesystem metadata syscalls, zlib/lzo/zstd libraries where enabled, and send-stream parsing from `common/send-stream`.
