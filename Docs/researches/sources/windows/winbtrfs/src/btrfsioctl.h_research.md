# File Research: sources/windows/winbtrfs/src/btrfsioctl.h

## Role

`btrfsioctl.h` is the public-ish WinBtrfs ioctl/FSCTL ABI header. It defines control codes and packed request/response structures used by user-mode tools and driver FSCTL handling.

## Control Codes

The file defines Btrfs-specific FSCTL/IOCTL values from function codes `0x829` through `0x84a`, including:

- File identity and metadata: `FSCTL_BTRFS_GET_FILE_IDS`, `GET_INODE_INFO`, `SET_INODE_INFO`, `GET_UUID`, `GET_CSUM_INFO`.
- Subvolume operations: create subvolume, create snapshot, received subvolume, reserve/find/send subvolume, read send buffer.
- Device and usage operations: get devices, get usage, add/remove device, resize, query filesystems, probe volume, unload.
- Balance operations: start/query/pause/resume/stop balance.
- Scrub operations: start/query/pause/resume/stop scrub.
- Unix-like metadata operations: `MKNOD`, get/set xattrs.
- Statistics: reset device stats.

## Data Structures

- File and inode reporting: `btrfs_get_file_ids`, `btrfs_inode_info`, and `btrfs_set_inode_info`.
- Snapshot/subvolume creation: `btrfs_create_snapshot`, `btrfs_create_snapshot32`, and `btrfs_create_subvol`; the 32-bit variants use `POINTER_32` to keep WOW64 ABI compatibility.
- Device/usage reporting: `btrfs_device`, `btrfs_usage_device`, `btrfs_usage`, `btrfs_filesystem_device`, and `btrfs_filesystem`.
- Balance: option flags, profile/range/limit/usage/convert filters in `btrfs_balance_opts`, status flags, `btrfs_query_balance`, and `btrfs_start_balance`.
- Scrub: status flags, per-error data/metadata union in `btrfs_scrub_error`, and aggregate `btrfs_query_scrub`.
- Unix/xattr/send/resize/checksum helpers: `btrfs_mknod`, `btrfs_received_subvol`, `btrfs_set_xattr`, `btrfs_find_subvol`, `btrfs_send_subvol`, `btrfs_send_subvol32`, `btrfs_resize`, and `btrfs_csum_info`.

## ABI Characteristics

- Many structs use trailing one-element arrays (`name[1]`, `devices[1]`, `data[1]`, `clones[1]`) for variable-length buffers.
- Wide-character names are used for Windows-facing names; raw `char` data is used for xattrs.
- The header includes `btrfs.h`, so public ioctl structures expose Btrfs types such as `BTRFS_UUID` and `KEY`.
- Compression constants in this file define the user-visible values for any/zlib/lzo/zstd.

## Research Notes

- This header is an ABI boundary. Field ordering, integer widths, pointer-size variants, and control-code values should be treated as stable.
- The methods vary by operation: many use direct I/O, xattr/send/find/csum use buffered I/O, and unload uses `METHOD_NEITHER`.
- The file explicitly says no copyright is claimed, unlike most driver implementation files.
