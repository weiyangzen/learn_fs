# File Research: sources/windows/winfsp/src/dll/security.c

Implements user-mode WinFsp access-check and security descriptor helpers around Windows security APIs.

Key globals/APIs:
- `FspFileGenericMapping`: maps generic file rights to `FILE_GENERIC_*` and `FILE_ALL_ACCESS`.
- `FspGetFileGenericMapping()`: exposes that mapping.

Core flow:
- `FspGetSecurityByName()` calls the file-system `GetSecurityByName` callback, reallocating the descriptor buffer on `STATUS_BUFFER_OVERFLOW`.
- `FspAccessCheckEx()` validates create requests and performs access checks for:
  - full target file access,
  - parent directory access,
  - main file access for named streams,
  - traverse access through each path component when the caller lacks traverse privilege.
- Reparse points are detected from returned attributes and converted to `STATUS_REPARSE` with the suffix index encoded in granted access.
- Parent checks can grant effective `DELETE` or `FILE_READ_ATTRIBUTES` through `FILE_DELETE_CHILD` or `FILE_LIST_DIRECTORY`, matching Windows semantics.
- Readonly files deny write/add/delete-child access and readonly delete-on-close yields `STATUS_CANNOT_DELETE`.

Descriptor lifecycle:
- `FspCreateSecurityDescriptor()` wraps `CreatePrivateObjectSecurity`, skips named-stream descriptors, and builds a child descriptor from an optional parent and create SD.
- `FspSetSecurityDescriptor()` works around `SetPrivateObjectSecurity` ownership expectations by copying the input SD onto the process heap before calling it.
- `FspDeleteSecurityDescriptor()` frees descriptors according to the creator path: `MemFree` for descriptors returned by access/Posix helpers, `DestroyPrivateObjectSecurity` for private-object APIs.

Important dependencies:
- File-system callback table: `FileSystem->Interface->GetSecurityByName`.
- Path helpers: `FspPathSuffix`, `FspPathCombine`, `FspPathSuffixIndex`.
- Windows APIs: `AccessCheck`, `CreatePrivateObjectSecurity`, `SetPrivateObjectSecurity`.
