# File Research: sources/os/linux/linux/fs/smb/common/smb2status.h

This header defines SMB2/NTSTATUS wire-status constants from MS-ERREF for the Linux SMB stack. It is data-oriented: after the include guard and `struct ntstatus`, the file is almost entirely `STATUS_*`, `DBG_*`, `RPC_NT_*`, and related constant definitions encoded with `cpu_to_le32()`.

The comments beside each status name carry the intended POSIX errno mapping, and the header explicitly notes that those comments feed generation of `smb2_error_map_table`. This makes the file both a protocol constant source and an error-translation source.

Important details:
- Defines severity constants and the packed `struct ntstatus` layout.
- Covers success, informational, warning, and error NTSTATUS ranges.
- Includes filesystem-relevant mappings such as `STATUS_OBJECT_NAME_NOT_FOUND`, `STATUS_ACCESS_DENIED`, `STATUS_SHARING_VIOLATION`, `STATUS_DISK_FULL`, `STATUS_NOT_A_DIRECTORY`, and `STATUS_STOPPED_ON_SYMLINK`.
- Ends with SMB-specific `STATUS_SMB_NO_PREAUTH_INTEGRITY_HASH_OVERLAP`.
- Has no executable logic, allocation, locking, or external calls.
