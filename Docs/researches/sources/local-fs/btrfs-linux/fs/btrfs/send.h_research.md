# File Research: sources/local-fs/btrfs-linux/fs/btrfs/send.h

## Purpose

`send.h` defines the Btrfs send stream wire protocol constants and packed headers used by `send.c` and receive-side consumers. It also declares the kernel ioctl entry point:

`long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`

## Stream Versioning

The stream magic is:

`BTRFS_SEND_STREAM_MAGIC "btrfs-stream"`

`BTRFS_SEND_STREAM_VERSION` is conditional:
- `3` when `CONFIG_BTRFS_EXPERIMENTAL` is enabled.
- `2` otherwise.

This means protocol v3 commands and attributes exist in the header but are only advertised as the maximum stream version for experimental builds.

Buffer sizes:
- `BTRFS_SEND_BUF_SIZE_V1` is `SZ_64K`.
- `BTRFS_SEND_BUF_SIZE_V2` is aligned to page size and sized for a 16 KiB command margin plus `BTRFS_MAX_COMPRESSED`.

## Packed Wire Headers

The file defines packed structures:
- `struct btrfs_stream_header`
  - stream magic,
  - little-endian version.
- `struct btrfs_cmd_header`
  - little-endian command payload length excluding header,
  - little-endian command ID,
  - CRC including the header with the CRC field zeroed during calculation.
- `struct btrfs_tlv_header`
  - little-endian TLV attribute type,
  - little-endian attribute length excluding the TLV header.

All multibyte fields are explicitly little-endian, matching the on-disk/on-stream Btrfs convention.

## TLV Type Kinds

`enum btrfs_tlv_type` defines generic value classes:
- unsigned integers: u8, u16, u32, u64,
- binary,
- string,
- UUID,
- Btrfs timespec.

These are type categories, not the command-specific attribute IDs.

## Commands

`enum btrfs_send_cmd` assigns stable command IDs.

Version 1 commands:
- subvolume/snapshot start,
- inode creation commands,
- rename/link/unlink/rmdir,
- set/remove xattr,
- write/clone,
- truncate/chmod/chown/utimes,
- end,
- update extent.

Version 2 commands:
- fallocate,
- file attributes,
- encoded write.

Version 3 command:
- enable fs-verity.

The file records version fences with:
- `BTRFS_SEND_C_MAX_V1`
- `BTRFS_SEND_C_MAX_V2`
- `BTRFS_SEND_C_MAX_V3`
- `BTRFS_SEND_C_MAX`

`send.c` uses these fences through `proto_cmd_ok()`.

## Attributes

The attribute enum defines command payload fields.

Version 1 attributes include:
- UUID and ctransid,
- inode metadata: inode number, size, mode, uid, gid, rdev, ctime, mtime, atime, otime,
- xattr name/data,
- path, destination path, link path,
- file offset,
- data payload,
- clone UUID, clone ctransid, clone path, clone offset, clone length.

`BTRFS_SEND_A_DATA` has a protocol note: in stream v2 it must be the last attribute in a command, has only the type in its header, and its length is implicit from the remaining command length. `send.c` implements this in `put_data_header()`.

Version 2 attributes include:
- fallocate mode,
- file attributes from the `FS_*_FL` namespace translated into Btrfs inode flags,
- encoded write metadata:
  - unencoded file length,
  - unencoded length,
  - unencoded offset,
  - compression,
  - encryption.

Compression and encryption default to none if omitted from an encoded write.

Version 3 attributes include:
- fs-verity algorithm,
- fs-verity block size,
- fs-verity salt data,
- fs-verity signature data.

The final maximum is `__BTRFS_SEND_A_MAX = 35`.

## Research Notes

This header is the protocol contract for Btrfs send. `send.c` enforces version compatibility against the command max constants and emits these packed headers/TLV attributes directly into the output stream. The most important compatibility detail is the v2 change to `BTRFS_SEND_A_DATA`, because it changes how data payload length is represented and requires data to be the final attribute.
