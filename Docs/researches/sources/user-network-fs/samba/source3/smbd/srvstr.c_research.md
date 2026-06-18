# sources/user-network-fs/samba/source3/smbd/srvstr.c

## Purpose
Provides a server-specific safe string push helper for encoding strings into SMB response buffers while mapping conversion errors to appropriate NTSTATUS values.

## Important APIs, Types, and Functions
`srvstr_push_fn()` wraps `push_string_base()`, accepts SMB flags, destination pointer/length, source string, conversion flags, and returns the encoded length through `ret_len`.

## Control Flow
The function rejects negative destination lengths, preserves the caller's `errno`, clears `errno`, calls `push_string_base()`, and interprets any resulting errno. Character conversion failures (`E2BIG`, `EILSEQ`, `EINVAL`) become `NT_STATUS_ILLEGAL_CHARACTER`; other errors are mapped through Unix-to-NT conversion, with `STATUS_MORE_ENTRIES` filtered to `NT_STATUS_UNSUCCESSFUL`. On success, it restores the saved errno and returns the pushed byte count.

## State and Persistence
No persistent state. It mutates the destination buffer and temporarily manipulates process-local `errno`.

## Dependencies and Integration Points
Depends on `push_string_base()` from string wrappers, SMB flags2 encoding behavior, Unix errno mapping, and smbd globals/includes. Used by SMB response construction paths that need bounded OEM/Unicode string encoding.

## Risks
Because success restores errno, callers must rely on NTSTATUS rather than errno after success. Conversion failures expose source string in debug logs. Incorrect `base_ptr` or flags can still produce protocol encoding bugs even with length protection.

## Test Signals
Test Unicode/OEM conversions, zero-length and negative destination lengths, too-small buffers, illegal byte sequences, errno preservation on success, and non-conversion errno mapping.
