# sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_close.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/file/file_close.c

Purpose: Demonstrates closing an open remote file handle by id with `NetFileClose()`.

Important APIs/types/functions: Parses hostname and numeric `fileid`; calls `NetFileClose(hostname, fileid)`.

Control flow: Initializes context, parses common options, requires hostname and file id arguments, converts the id with `atoi()`, calls the API, reports the libnetapi error string on failure, and releases context/popt state.

State and persistence behavior: The remote server state changes by closing a listed open file. No local files are persisted.

Dependencies and integration points: Complements `file_enum` and `file_getinfo` examples for server open-file administration.

Risks: `atoi()` lacks validation and may treat malformed ids as zero. Operation is administrative and can disrupt remote users.

Test signals: Enumerate open files, close a test file id, then re-enumerate to confirm removal.
