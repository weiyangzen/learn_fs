# sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_enum.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/share/share_enum.c

Purpose: Demonstrates paged share enumeration with `NetShareEnum()`.

Important APIs/types/functions: Supports levels 0, 1, and 2 using `SHARE_INFO_0/1/2`, resume handle, entries read, and total entries.

Control flow: Parses hostname and level, loops on success or `ERROR_MORE_DATA`, prints share names and level-specific type/remark/permission/path/user fields, frees buffers, and handles final status.

State and persistence behavior: Read-only remote share query.

Dependencies and integration points: Verifies share add/delete/set operations.

Risks: Level 2 may expose paths and share passwords if a server returns them. Large enumerations rely on resume progress.

Test signals: Enumerate known shares at levels 0-2 and verify new share visibility.
