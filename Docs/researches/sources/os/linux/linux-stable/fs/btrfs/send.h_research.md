# File Research: sources/os/linux/linux-stable/fs/btrfs/send.h

## Purpose

`send.h` defines the public Btrfs send stream format constants used by kernel send generation and userspace receive parsing. It also declares the ioctl entry point:

- `long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`

## Protocol Versioning

The stream magic is `btrfs-stream`.

`BTRFS_SEND_STREAM_VERSION` is:

- `3` when `CONFIG_BTRFS_EXPERIMENTAL` is enabled
- `2` otherwise

Buffer sizing is version-dependent:

- v1 commands are bounded by `BTRFS_SEND_BUF_SIZE_V1`, 64 KiB
- v2 uses `BTRFS_SEND_BUF_SIZE_V2`, aligned to fit a command header plus maximum compressed extent payload

## Wire Structures

The header defines packed stream wire structures:

- `struct btrfs_stream_header`: magic plus little-endian stream version
- `struct btrfs_cmd_header`: command payload length, command ID, and CRC
- `struct btrfs_tlv_header`: attribute type and attribute length

`enum btrfs_tlv_type` documents supported value classes: integer widths, binary, string, UUID, and timespec.

## Commands

`enum btrfs_send_cmd` defines stream command IDs.

Version 1 commands include subvolume/snapshot creation, inode creation types, rename/link/unlink/rmdir, xattr set/remove, write, clone, truncate, chmod, chown, utimes, end, and update extent.

Version 2 adds:

- `BTRFS_SEND_C_FALLOCATE`
- `BTRFS_SEND_C_FILEATTR`
- `BTRFS_SEND_C_ENCODED_WRITE`

Version 3 adds:

- `BTRFS_SEND_C_ENABLE_VERITY`

The enum also records max command IDs per protocol version.

## Attributes

The send attribute enum defines TLV attribute IDs.

Version 1 attributes cover UUIDs, transaction IDs, inode metadata, timestamps, xattr name/data, paths, file offsets, write data, and clone source metadata.

Version 2 adds:

- fallocate mode
- Btrfs inode file attributes
- encoded write unencoded length/offset metadata
- compression and encryption fields

`BTRFS_SEND_A_DATA` has special v2 behavior: it must be the final command attribute, its header carries only the type, and its length is implicitly the remaining command length.

Version 3 adds fs-verity attributes:

- hash algorithm
- block size
- salt data
- signature data

## Integration Notes

This header is the format contract consumed by `send.c`. Any changes to command IDs, attribute IDs, packed structures, or max-version constants affect stream compatibility with userspace receive tools and older kernels. New features must be protocol-gated, as `send.c` does for fallocate, file attributes, encoded writes, and verity.
