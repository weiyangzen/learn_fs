# File Research: sources/local-fs/kdave-linux/fs/btrfs/send.h

## Scope

`send.h` defines the Btrfs send-stream wire constants, command and attribute IDs, TLV/header layouts, protocol-version limits, buffer sizing, and the kernel-internal declaration for `btrfs_ioctl_send()`.

## Interfaces And Constants

- Stream identity: `BTRFS_SEND_STREAM_MAGIC` and `BTRFS_SEND_STREAM_VERSION`.
- Protocol version selection is conditional: version 3 is exposed only with `CONFIG_BTRFS_EXPERIMENTAL`; otherwise the maximum is version 2.
- Buffer sizes: v1 uses `BTRFS_SEND_BUF_SIZE_V1` at 64 KiB; v2 uses `BTRFS_SEND_BUF_SIZE_V2`, aligned to fit command overhead plus maximum compressed extent payload.
- Wire structs: `struct btrfs_stream_header`, `struct btrfs_cmd_header`, and `struct btrfs_tlv_header`, all packed and little-endian.
- TLV type enum describes expected value encodings: integers, binary, string, UUID, and Btrfs timespec.
- Public declaration: `long btrfs_ioctl_send(struct btrfs_root *send_root, const struct btrfs_ioctl_send_args *arg);`.

## Command Space

- Version 1 commands cover subvol/snapshot creation, file and special-file creation, symlink, rename/link/unlink/rmdir, xattr updates, write/clone, truncate/chmod/chown/utimes, END, and update-extent.
- Version 2 adds fallocate, file-attribute updates, and encoded writes.
- Version 3 adds enable-verity.
- `BTRFS_SEND_C_MAX_V1`, `_V2`, `_V3`, and `BTRFS_SEND_C_MAX` define protocol-specific command ceilings used by `send.c`.

## Attribute Space

- Version 1 attributes cover UUIDs, ctransids, inode metadata, xattr name/data, paths, write offsets/data, and clone source metadata.
- `BTRFS_SEND_A_DATA` has a v2+ special encoding: it must be the final command attribute and its length is implied by the remaining command bytes.
- Version 2 adds fallocate mode, Btrfs inode file attributes, unencoded lengths/offsets, compression, and encryption metadata for encoded writes.
- Version 3 adds verity algorithm, block size, salt, and signature data.

## Dependencies

- Includes Linux scalar/size/alignment headers and forward-declares `struct btrfs_root` and `struct btrfs_ioctl_send_args`.
- Consumed by `send.c` for stream construction and by any internal caller needing the ioctl implementation declaration.

## Risks And Invariants

- Command and attribute numeric values are wire format and must remain stable for userspace receive compatibility.
- Packed little-endian headers are part of the stream ABI.
- Protocol-gated maximum constants must stay synchronized with the enums, `proto_cmd_ok()` logic, and userspace receiver support.
- The v2 data-attribute special case constrains command-building order: payload data must be emitted last.
