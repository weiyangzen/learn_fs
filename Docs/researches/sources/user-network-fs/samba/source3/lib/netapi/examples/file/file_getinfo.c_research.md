# sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_getinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_getinfo.c

Purpose: Demonstrates querying one open remote file record by id with `NetFileGetInfo()`.

Important APIs/types/functions: Accepts hostname, file id, and level. Prints `FILE_INFO_2` id or `FILE_INFO_3` id, permissions, lock count, path, and username.

Control flow: Initializes, parses options and positional args, converts id/level through `atoi()`, calls `NetFileGetInfo()`, switches on level, prints known structures, frees the API buffer, and cleans up.

State and persistence behavior: Read-only remote server query; local state is limited to allocated result buffer.

Dependencies and integration points: Pairs with `file_enum` output, where ids can be discovered.

Risks: Invalid levels silently produce no detail after successful calls. Numeric parsing is weak.

Test signals: Query ids from `file_enum` at levels 2 and 3 and verify error path for a nonexistent id.
