# File Research: sources/os/linux/linux/fs/btrfs/send.h

## Purpose

`send.h` defines the public Btrfs send stream wire-format constants used by `send.c` and the ioctl entry declaration.

It contains:

- Stream magic and protocol version selection.
- Send buffer size constants.
- Packed wire-format headers.
- Send command IDs.
- Send attribute IDs.
- `btrfs_ioctl_send()` declaration.

## Protocol Versioning

`BTRFS_SEND_STREAM_MAGIC` is `"btrfs-stream"`.

`BTRFS_SEND_STREAM_VERSION` is:

- `3` when `CONFIG_BTRFS_EXPERIMENTAL` is enabled.
- `2` otherwise.

Protocol support is split by command and attribute maximums:

- v1 max command: `BTRFS_SEND_C_UPDATE_EXTENT`
- v2 adds fallocate, file attributes, and encoded writes.
- v3 adds fs-verity enable support.

## Buffer Sizes

The header defines:

- `BTRFS_SEND_BUF_SIZE_V1` as `SZ_64K`.
- `BTRFS_SEND_BUF_SIZE_V2` as `ALIGN(SZ_16K + BTRFS_MAX_COMPRESSED, PAGE_SIZE)`.

The v2 buffer is sized for command overhead plus a maximum compressed extent payload.

## Wire Headers

Packed structures:

- `struct btrfs_stream_header`
  - magic string
  - little-endian stream version

- `struct btrfs_cmd_header`
  - payload length excluding header
  - command ID
  - CRC including header with zeroed CRC field

- `struct btrfs_tlv_header`
  - attribute type
  - attribute length excluding the TLV header

These structures are serialized directly into the send stream, so packing and little-endian fields are part of the ABI.

## Commands

`enum btrfs_send_cmd` defines send stream command IDs.

v1 commands include:

- Subvolume/snapshot creation metadata.
- Inode creation commands: file, dir, node, fifo, socket, symlink.
- Namespace operations: rename, link, unlink, rmdir.
- Xattr operations.
- File data operations: write, clone.
- Metadata operations: truncate, chmod, chown, utimes.
- End and update extent.

v2 commands add:

- `BTRFS_SEND_C_FALLOCATE`
- `BTRFS_SEND_C_FILEATTR`
- `BTRFS_SEND_C_ENCODED_WRITE`

v3 adds:

- `BTRFS_SEND_C_ENABLE_VERITY`

`BTRFS_SEND_C_MAX` currently aliases the v3 maximum.

## Attributes

The attribute enum defines TLV IDs used by commands.

v1 attributes include:

- UUIDs and ctransids.
- Inode metadata: ino, size, mode, uid, gid, rdev, times.
- Xattr name/data.
- Paths and link paths.
- File offset and file data.
- Clone source identity/path/offset/length.

Important note: starting with stream v2, `BTRFS_SEND_A_DATA` is special. It must be the last attribute in a command, and its length is implicit from the remaining command length rather than stored in a normal TLV length field.

v2 attributes add:

- fallocate mode
- file attributes
- unencoded length/offset metadata for encoded writes
- compression and encryption fields

v3 attributes add:

- verity algorithm
- verity block size
- verity salt
- verity signature

## External Interface

The only function declared is:

`long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`

This is implemented in `send.c` and is the kernel entry point for producing a send stream.

## Research Notes

This header is the ABI map for Btrfs send streams. Most compatibility logic lives in `send.c`, but this file defines the stable numeric command and attribute layout that both kernel send and userspace receive must understand.
