# sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_enum.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_enum.c

Purpose: Demonstrates paged enumeration of open files on a remote server with `NetFileEnum()`.

Important APIs/types/functions: Handles levels 2 and 3, `FILE_INFO_2`, `FILE_INFO_3`, resume handles, `entries_read`, and `total_entries`.

Control flow: Parses hostname, optional base path/user/level, then loops while status is success or `ERROR_MORE_DATA`. Each page casts the returned buffer by level, prints file ids and level-specific lock/path/user fields, frees the buffer, and continues with the resume handle.

State and persistence behavior: Read-only remote administrative query. Resume handle maintains server-side enumeration position.

Dependencies and integration points: Uses common libnetapi context and NetAPI buffer ownership.

Risks: Only levels 2 and 3 are printed. Resume loops depend on server returning progress. Optional path/user filters are positional and easy to omit incorrectly.

Test signals: Run against a server with known open files, with and without path/user filters, and force multi-page enumeration.
