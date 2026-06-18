<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.c -->
# sources/user-network-fs/samba/source3/lib/util_ea.c

## Purpose
`util_ea.c` parses SMB extended attribute buffers into Samba `ea_list` structures.

## Important APIs, types, and functions
Public functions are `read_ea_list_entry` for one EA entry and `read_nttrans_ea_list` for NT transact EA lists.

## Control flow
`read_ea_list_entry` validates minimum header length, reads flags/name length/value length, checks bounds, requires a null-terminated ASCII EA name, converts the name, allocates a value blob with an extra null byte, copies the value, and reports bytes consumed. `read_nttrans_ea_list` walks an EA list where each item is preceded by a next-offset field, appends parsed entries with `DLIST_ADD_END`, and stops on zero next offset.

## State and persistence behavior
The functions allocate talloc-owned in-memory lists only. They do not read or write filesystem EAs.

## Dependencies and integration points
The file depends on SMB byte macros, talloc, ASCII pull conversion, `DATA_BLOB`, debug dumping, and the `ea_list` type used by SMB transaction handling.

## Risks and edge cases
Bounds checks protect against truncated buffers and integer wrap while advancing offsets. Name conversion failure logs but still relies on `eal->ea.name` being non-null for success. Value blobs are null-padded for safe debug printing, but the stored length excludes the terminator.

## Test signals
Tests should cover truncated headers, non-null-terminated names, value bounds, multiple-entry next-offset traversal, zero offset termination, and wrap-protection branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.c -->
