# File Research: sources/os/linux/linux-stable/fs/smb/client/nterr.h

Read status: complete.

## Purpose

Defines NTSTATUS and selected Win32 error constants used by CIFS/SMB error mapping and protocol handling.

## Main Contents

- Include guard `_NTERR_H`.
- `struct ntstatus_to_dos_err`
  - Maps an NT status to DOS error class/code and a string name.
- Win32 error constants:
  - `NT_ERROR_INVALID_PARAMETER`
  - `NT_ERROR_INSUFFICIENT_BUFFER`
  - `NT_ERROR_INVALID_DATATYPE`
- Large `NT_STATUS_*` constant set.
  - Includes success/pending statuses, informational statuses, warnings, and many `0xC0000000` failure statuses.
  - Covers object/path errors, access errors, pipe errors, network errors, domain/logon errors, DFS/path-not-covered errors, reparse/encryption statuses, and SMB/auth-related statuses.
- Per-constant comments encode DOS error class/code mapping data used to generate `smb1_mapping_table.c`.

## Important Groups

- General operation:
  - `NT_STATUS_OK`, `NT_STATUS_PENDING`, `NT_STATUS_MORE_ENTRIES`, `NT_STATUS_BUFFER_OVERFLOW`, `NT_STATUS_NO_MORE_ENTRIES`.

- File/path/object:
  - `NT_STATUS_NO_SUCH_FILE`, `NT_STATUS_OBJECT_NAME_NOT_FOUND`, `NT_STATUS_OBJECT_NAME_COLLISION`, `NT_STATUS_OBJECT_PATH_NOT_FOUND`, `NT_STATUS_DELETE_PENDING`, `NT_STATUS_DIRECTORY_NOT_EMPTY`, `NT_STATUS_NOT_A_DIRECTORY`, `NT_STATUS_NAME_TOO_LONG`.

- Access/security:
  - `NT_STATUS_ACCESS_DENIED`, `NT_STATUS_PRIVILEGE_NOT_HELD`, `NT_STATUS_INVALID_OWNER`, `NT_STATUS_INVALID_SID`, `NT_STATUS_INVALID_SECURITY_DESCR`, `NT_STATUS_LOGON_FAILURE`, `NT_STATUS_ACCOUNT_DISABLED`, `NT_STATUS_ACCOUNT_LOCKED_OUT`.

- Locking/sharing/oplocks:
  - `NT_STATUS_SHARING_VIOLATION`, `NT_STATUS_FILE_LOCK_CONFLICT`, `NT_STATUS_LOCK_NOT_GRANTED`, `NT_STATUS_OPLOCK_NOT_GRANTED`, `NT_STATUS_INVALID_OPLOCK_PROTOCOL`.

- Network/share/session:
  - `NT_STATUS_BAD_NETWORK_PATH`, `NT_STATUS_NETWORK_BUSY`, `NT_STATUS_BAD_NETWORK_NAME`, `NT_STATUS_NETWORK_NAME_DELETED`, `NT_STATUS_CONNECTION_DISCONNECTED`, `NT_STATUS_NETWORK_SESSION_EXPIRED`.

- DFS/reparse/encryption:
  - `NT_STATUS_PATH_NOT_COVERED`, `NT_STATUS_NOT_A_REPARSE_POINT`, `NT_STATUS_DIRECTORY_IS_A_REPARSE_POINT`, `NT_STATUS_ENCRYPTION_FAILED`, `NT_STATUS_DECRYPTION_FAILED`.

- SMB/auth negotiation:
  - `NT_STATUS_MORE_PROCESSING_REQUIRED`, `NT_STATUS_NO_USER_SESSION_KEY`, `NT_STATUS_NO_PREAUTH_INTEGRITY_HASH_OVERLAP`.

## Dependencies

- Uses fixed-width kernel integer types.
- Consumed by CIFS error mapping code and protocol handlers that compare raw NTSTATUS values.

## Notable Behaviors

- This header is data definition only; it contains no executable logic.
- Comments are part of the build/data-generation contract for SMB1 NTSTATUS-to-DOS mapping.
