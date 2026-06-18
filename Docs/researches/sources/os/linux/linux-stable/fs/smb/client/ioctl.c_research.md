# File Research: sources/os/linux/linux-stable/fs/smb/client/ioctl.c

Read status: complete.

## Purpose

Implements CIFS/SMB file ioctl handling for filesystem flags, server-side copy, query-info passthrough, integrity/compression controls, snapshot enumeration, mount information, encryption key debug export, notifications, and forced shutdown.

## Main Responsibilities

- Dispatch `cifs_ioctl()` commands from VFS to CIFS/SMB-specific operations.
- Convert pathnames for query-info ioctl use.
- Support server-side copychunk from another CIFS file descriptor.
- Report mount, tree-connect, share, filesystem, and protocol information to userspace.
- Implement XFS-style going-down shutdown semantics for CIFS mounts.
- Export SMB3 encryption key material to privileged callers for debugging.
- Wire directory change-notification ioctls to dialect-specific notify operations.

## Important Functions

- `cifs_ioctl_query_info()`
  - Builds the dentry path, converts it to UTF-16, handles root path specially, and calls `server->ops->ioctl_query_info`.

- `cifs_ioctl_copychunk()`
  - Validates destination write mode and mount writability.
  - Validates that the source fd is also a CIFS file and not a directory.
  - Copies the full source size through `cifs_file_copychunk_range()`.

- `smb_mnt_get_tcon_info()`
  - Copies tree id and session id to userspace.

- `smb_mnt_get_fsinfo()`
  - Reports protocol id, tcon flags, device characteristics, filesystem attributes, volume serial/create time, share flags/capabilities, sector flags, optimal sector size, maximal access, chunk size, and CIFS POSIX capability bits.

- `cifs_shutdown()`
  - Requires `CAP_SYS_ADMIN`.
  - Accepts logflush/nologflush style shutdown flags and sets `CIFS_MOUNT_SHUTDOWN`.
  - Rejects unsupported default flush semantics.

- `cifs_dump_full_key()`
  - Validates encryption state and optional session id.
  - Finds a matching session when requested, sizes key output for AES-128 or AES-256 variants, and copies session, encryption, and decryption keys to userspace.

- `cifs_ioctl()`
  - Main command dispatcher.
  - Handles `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `CIFS_IOC_COPYCHUNK_FILE`, `CIFS_QUERY_INFO`, `CIFS_IOC_SET_INTEGRITY`, mount info ioctls, snapshot enumeration, key dumps, notifications, and shutdown.

## Dependencies

- Uses `cifs_ioctl.h` ioctl structures, dialect operations from `server->ops`, CIFS session/tcon state, SMB2/SMB3 encryption metadata, Linux fd helpers, mount write accounting, and userspace copy helpers.

## Notable Behaviors

- Compression is the only generic file flag set path currently implemented through `FS_IOC_SETFLAGS`.
- Legacy `CIFS_DUMP_KEY` only handles fixed AES-128-era key sizes; `CIFS_DUMP_FULL_KEY` handles variable key sizes.
- Key-dump ioctls are gated by `CAP_SYS_ADMIN`; shutdown is also privileged.
- Unsupported ioctls return `-ENOTTY`, matching existing ioctl precedent.
