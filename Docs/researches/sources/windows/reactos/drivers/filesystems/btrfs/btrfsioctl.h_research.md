# File Research: sources/windows/reactos/drivers/filesystems/btrfs/btrfsioctl.h

## Purpose

Public Btrfs IOCTL/FSCTL ABI header for user/kernel communication with the Btrfs driver. It defines Btrfs-specific control codes and the request/response structures used for subvolume management, inode metadata, device listing, usage reporting, balance, scrub, xattrs, send/receive, resize, and checksum queries.

## Main Contents

- Control codes:
  - `FSCTL_BTRFS_GET_FILE_IDS`
  - `FSCTL_BTRFS_CREATE_SUBVOL`
  - `FSCTL_BTRFS_CREATE_SNAPSHOT`
  - `FSCTL_BTRFS_GET_INODE_INFO`
  - `FSCTL_BTRFS_SET_INODE_INFO`
  - `FSCTL_BTRFS_GET_DEVICES`
  - `FSCTL_BTRFS_GET_USAGE`
  - Balance controls: start/query/pause/resume/stop.
  - Device controls: add/remove.
  - Filesystem enumeration/probing/unload controls.
  - Scrub controls: start/query/pause/resume/stop.
  - Stats reset, `mknod`, received subvolume, xattr get/set, reserve/find/send/read-send-buffer, resize, checksum info.
- Compression constants:
  - `BTRFS_COMPRESSION_ANY`
  - `BTRFS_COMPRESSION_ZLIB`
  - `BTRFS_COMPRESSION_LZO`
  - `BTRFS_COMPRESSION_ZSTD`
- User-visible structures:
  - File identity: `btrfs_get_file_ids`.
  - Snapshot/subvolume creation: `btrfs_create_snapshot`, `btrfs_create_snapshot32`, `btrfs_create_subvol`.
  - Inode metadata: `btrfs_inode_info`, `btrfs_set_inode_info`.
  - Device and filesystem enumeration: `btrfs_device`, `btrfs_usage_device`, `btrfs_usage`, `btrfs_filesystem_device`, `btrfs_filesystem`.
  - Balance: `btrfs_balance_opts`, `btrfs_start_balance`, `btrfs_query_balance`.
  - Scrub: `btrfs_scrub_error`, `btrfs_query_scrub`.
  - Unix node creation and receive metadata: `btrfs_mknod`, `btrfs_received_subvol`.
  - Xattrs: `btrfs_set_xattr`.
  - Send/receive: `btrfs_find_subvol`, `btrfs_send_subvol`, `btrfs_send_subvol32`.
  - Resize and checksum export: `btrfs_resize`, `btrfs_csum_info`.

## ABI Notes

- Several structures use trailing one-element arrays (`name[1]`, `devices[1]`, `errors`, `data[1]`) as variable-length payloads.
- 32-bit compatibility structures use `POINTER_32` for handles/pointers passed from WOW64-style callers.
- Uses Windows `BOOL`, `HANDLE`, `WCHAR`, `ULONG`, `USHORT`, `NTSTATUS`, and Btrfs fixed-width integer fields.
- Balance and scrub status constants are bit/status values consumed by management tools and `fsctl.c` handlers.

## Dependencies

- Includes `btrfs.h` for Btrfs UUID and on-disk-compatible types.
- Included by `btrfs_drv.h`, so all driver modules see these definitions.
- Control codes are handled primarily by filesystem/device-control code outside this file.

## Research Notes

- This file is ABI-sensitive. Field order, widths, alignment assumptions, control numbers, and variable-length buffer conventions must remain stable for user-mode tools.
- `btrfs_inode_info` includes per-compression disk usage fields for zlib, LZO, Zstd, sparse size, and extent count, making it a metadata reporting interface rather than just POSIX stat emulation.
