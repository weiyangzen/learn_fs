<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.h -->
# sources/user-network-fs/samba/source3/lib/util_ea.h

## Purpose
This header declares SMB extended attribute buffer parsing helpers.

## Important APIs, types, and functions
It exposes `read_ea_list_entry` and `read_nttrans_ea_list`, both returning `struct ea_list *` allocated under a caller-provided talloc context.

## Control flow
Callers parse one entry when they track offsets themselves or parse a complete NT transact EA list in one call.

## State and persistence behavior
The header has no state and promises in-memory parse results only.

## Dependencies and integration points
It is included by SMB server request code that decodes client-supplied EA buffers.

## Risks and edge cases
Callers must treat NULL returns as malformed input or allocation failure and avoid partially using an EA list.

## Test signals
Compile coverage verifies prototypes; parser behavior is covered through `util_ea.c` tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/lib/util_ea.h -->
