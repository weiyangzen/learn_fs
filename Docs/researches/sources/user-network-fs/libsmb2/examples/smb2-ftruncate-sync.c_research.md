# sources/user-network-fs/libsmb2/examples/smb2-ftruncate-sync.c

Purpose: This synchronous example opens a remote SMB file and changes its length through a file handle.

Important APIs and types: It uses `smb2_connect_share`, `smb2_open` with `O_RDWR`, `smb2_ftruncate`, `smb2_close`, and URL/context cleanup. The new length is parsed with `strtoll`.

Control flow: After argument and URL parsing, the program connects to the share, opens the remote path read/write, calls `smb2_ftruncate` with the requested length, closes the handle, disconnects, and exits.

State and persistence behavior: The persistent effect is remote file size mutation on the SMB server. Local state is limited to the SMB context, URL, and file handle.

Dependencies and integration points: It demonstrates handle-based truncation and validates create/open access rights required for file-size modification.

Risks: Length parsing has no validation for invalid strings, overflow, or negative values. Error branches may exit without disconnecting. The operation is destructive to remote file contents beyond the new EOF.

Test signals: Stat the remote file before and after truncation, test expansion and shrinkage, and verify access-denied behavior on read-only files.
