# File Research: sources/os/linux/linux-stable/fs/smb/common/smb2status.h

Read status: complete.

## Purpose
Defines little-endian SMB2/NTSTATUS status constants from MS-ERREF for use across SMB client/server error handling.

## Main Contents
- NTSTATUS severity constants and `struct ntstatus`.
- A large catalog of `STATUS_*`, `RPC_NT_*`, `DBG_*`, and subsystem-specific status codes.
- End-of-line comments documenting the intended Linux/POSIX errno mapping used to generate `smb2_error_map_table`.

## Dependencies And Role
This is a shared protocol header under `fs/smb/common`, consumed by SMB2/SMB3 code that emits, parses, or maps wire status values. Constants are stored with `cpu_to_le32()`/`__constant_cpu_to_le32()` so callers can compare or place wire-format status values directly.

## Risks
The main risk is status-to-errno drift: the comments are not passive documentation, they feed generated mapping tables. Any new code or renamed constants must preserve little-endian representation and keep mappings aligned with SMB2 client/server behavior.
