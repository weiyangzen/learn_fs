# sources/user-network-fs/libsmb2/examples/smb2-put-async.c

Purpose: This example uploads a local file to an SMB path using asynchronous writes.

Important APIs and types: It uses POSIX `open`, `read`, `close`, libsmb2 `smb2_connect_share`, `smb2_open`, `smb2_pwrite_async`, `smb2_service`, and a callback state structure containing local fd, remote handle, position, and completion flag.

Control flow: The program opens the local file, connects synchronously to the SMB share, opens/creates the remote file, reads the first 1024-byte block locally, queues an async pwrite, then polls until write callbacks read and queue subsequent chunks. A status of zero marks upload completion before cleanup.

State and persistence behavior: Persistent effects are a remote file created or overwritten/extended at the destination path. Runtime state includes local fd, SMB file handle, offset, buffer, and callback completion.

Dependencies and integration points: It demonstrates mixing synchronous connect/open with asynchronous write and event servicing.

Risks: `argc` validation checks only `< 2` even though `argv[2]` is required, so missing URL can access out of bounds. The write callback treats local EOF (`read <= 0`) as fatal instead of closing cleanly after the final successful write; completion relies on an async write status of zero. It writes fixed 1024-byte chunks despite a larger buffer.

Test signals: Upload a known local file and compare remote contents. Test zero-length files, missing URL, local EOF after last chunk, and network write errors.
