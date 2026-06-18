# sources/user-network-fs/samba/source3/smbd/error.c

## Purpose
`error.c` builds SMB1 error replies and selects whether errors are sent as NTSTATUS or legacy DOS error class/code values.

## Important APIs, types, and functions
- `use_nt_status()` returns whether NTSTATUS replies are enabled and the client advertised `CAP_STATUS32`.
- `error_packet_set()` writes NT or DOS error fields into an SMB1 outbuf and updates `FLAGS2_32_BIT_ERROR_CODES`.
- `error_packet()` creates a minimal SMB1 error packet and delegates to `error_packet_set()`.
- `reply_nt_error()`, `reply_force_dos_error()`, and `reply_both_error()` reset the request outbuf and install the desired error.
- `reply_openerror()` preserves specific Windows-compatible mappings for object-name collision and too-many-open-files.

## Control flow
Callers can request pure NT status, forced DOS status, or a combined NT/DOS mapping. If eclass is `-1`, NT status is forced. If `ntstatus` is an encoded DOS status, DOS is forced. Otherwise Samba sends NT status only when both server configuration and client capability allow it; legacy clients receive DOS class/code. For DOS replies, `ntstatus_to_dos()` maps NT status when needed. For NT replies, `dos_to_ntstatus()` maps nonzero DOS inputs when no NT status was supplied.

## State and persistence behavior
This file mutates only outgoing SMB1 response buffers. It reads global client capabilities and loadparm status support.

## Dependencies and integration points
It depends on SMB1 buffer macros, error mapping helpers, request output buffer helpers, and optional SMB1 command name lookup. All SMB1 reply paths that need error packets use these helpers or macros wrapping them.

## Risks and edge cases
- Wire compatibility depends on special mappings in `reply_openerror()`, especially `NT_STATUS_OBJECT_NAME_COLLISION` and `NT_STATUS_TOO_MANY_OPENED_FILES`.
- Debug messages avoid starting with the word `error` to keep subunit test streams clean.
- Forced DOS and forced NT modes are encoded through sentinel values and must be used consistently by macros.

## Test signals
Tests should verify NT-capable and legacy client replies, forced DOS behavior, DOS-to-NT and NT-to-DOS mappings, `FLAGS2_32_BIT_ERROR_CODES` changes, and `reply_openerror()`'s special mappings.
