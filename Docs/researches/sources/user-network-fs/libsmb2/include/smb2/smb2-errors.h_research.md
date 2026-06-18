# sources/user-network-fs/libsmb2/include/smb2/smb2-errors.h

## Purpose
`smb2-errors.h` defines NTSTATUS severity masks and a large set of SMB2/Windows status constants used by libsmb2.

## Important APIs, Types, and Functions
The header defines severity/customer/facility/code masks and constants such as `SMB2_STATUS_SUCCESS`, `SMB2_STATUS_PENDING`, `SMB2_STATUS_NO_MORE_FILES`, `SMB2_STATUS_ACCESS_DENIED`, `SMB2_STATUS_OBJECT_NAME_NOT_FOUND`, `SMB2_STATUS_LOGON_FAILURE`, `SMB2_STATUS_IO_TIMEOUT`, `SMB2_STATUS_NOT_SUPPORTED`, `SMB2_STATUS_CANCELLED`, `SMB2_STATUS_BUFFER_OVERFLOW`, and many others.

## Control Flow
There is no executable control flow. Runtime code compares SMB response status values against these macros and maps them through `nterror_to_str()` or `nterror_to_errno()` declared in `libsmb2.h`.

## State and Persistence Behavior
No state or persistence. The constants are compile-time protocol definitions.

## Dependencies and Integration Points
`smb2.h` includes this header, making the constants available to public protocol structs and callers. Error handling in raw and high-level APIs depends on these values.

## Risks and Edge Cases
Coverage is broad but static; missing newer NTSTATUS values may map poorly. The custom `SMB2_STATUS_SHUTDOWN` value is `0xffffffff`, outside normal NTSTATUS success/error classes. Macro-only definitions provide no type safety.

## Test Signals
Verify NTSTATUS-to-errno/string mappings for common authentication, path, sharing, timeout, EOF, and no-more-files statuses. Test unknown status handling.
