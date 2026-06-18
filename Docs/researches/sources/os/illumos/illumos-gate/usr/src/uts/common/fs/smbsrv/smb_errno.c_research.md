# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_errno.c

## Role

Provides error translation helpers between illumos `errno`, NT status codes, and SMB1 DOS/Win32 error codes.

## Major Responsibilities

- Maps common Unix errors to NT status values.
- Converts NT status values to 16-bit Win32/DOS-style error codes suitable for SMB1 DOS error replies.
- Falls back to internal/general failure errors when no mapping exists.

## Key Functions

- `smb_errno2status()` returns an NT status for an `errno`, with explicit mappings for access, path, handle, quota, disk-full, stale-handle, invalid-name, and lock-conflict cases.
- `smb_status2doserr()` searches `smb_status2winerr_map` and returns only Win32 errors that fit below `0xFFFF`, otherwise `ERROR_GEN_FAILURE`.

## Research Notes

This file is intentionally small but central to consistent SMB1 error behavior. `ERANGE` is specially used for byte-range lock conflicts and maps to `NT_STATUS_FILE_LOCK_CONFLICT`.
