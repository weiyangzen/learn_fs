<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_api.c -->
# sources/storage-engines/wiredtiger/src/packing/pack_api.c

## Purpose
Exposes public and extension varargs wrappers for WiredTiger's structure packing, sizing, and unpacking APIs.

## Important APIs, Types, and Functions
`wiredtiger_struct_pack`, `wiredtiger_struct_size`, `wiredtiger_struct_unpack`, plus extension methods `__wt_ext_struct_pack`, `__wt_ext_struct_size`, and `__wt_ext_struct_unpack`.

## Control Flow
Each wrapper converts `WT_SESSION` to `WT_SESSION_IMPL`, starts a `va_list`, delegates to the corresponding `__wt_struct_*v` implementation, ends the `va_list`, and returns the result. Extension wrappers use the connection default session when the extension passes NULL.

## State and Persistence Behavior
Only caller-provided buffers are packed/unpacked; no persistent metadata is written.

## Dependencies and Integration Points
This is the ABI-facing shim over internal pack implementation used by applications and extensions.

## Risks and Edge Cases
Varargs must match the format string exactly; this layer cannot type-check them. NULL extension sessions intentionally use the default session, which affects error context and allocation.

## Test Signals
API compatibility tests, extension NULL-session paths, varargs format mismatch errors, and boundary buffer sizes are important.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/packing/pack_api.c -->
