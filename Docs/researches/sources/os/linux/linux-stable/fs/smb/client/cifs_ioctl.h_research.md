# File Research: sources/os/linux/linux-stable/fs/smb/client/cifs_ioctl.h

## Purpose

Defines userspace ABI structures and ioctl numbers for CIFS/SMB3 mount information, tcon information, snapshots, passthrough query/set/fsctl operations, debug key dumping, notifications, copychunk, integrity, and shutdown.

## Main Contents

- `struct smb_mnt_fs_info`
  - Packed mount/share/filesystem metadata including version, protocol, tcon flags, volume serial/time, share caps/flags, sector info, chunk size, filesystem attributes, component length, device type/characteristics, maximal access, and POSIX capabilities.
- `struct smb_mnt_tcon_info`
  - Packed tree ID and session ID.
- `struct smb_snapshot_array`
  - Snapshot enumeration header with flexible trailing snapshot data.
- `struct smb_query_info`
  - Passthrough query/set/fsctl parameters plus variable trailing buffer.
- `struct smb3_key_debug_info`
  - Legacy fixed-size key dump structure for common 16-byte keys.
- `struct smb3_full_key_debug_info`
  - Variable-size key dump structure supporting longer session/encryption keys.
- `struct smb3_notify` and `struct smb3_notify_info`
  - Change-notify request and response structures.
- Defines ioctl numbers using magic `0xCF` for CIFS operations and `'X',125` for shutdown.
- Defines shutdown behavior flags:
  - default
  - log flush only
  - no log flush

## Security and ABI Notes

- Key dump ioctls intentionally expose session/encryption key material and should be gated by build/runtime policy in users of this header.
- All structs are packed, making field ordering and sizes ABI-sensitive.
