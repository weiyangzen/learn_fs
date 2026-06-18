# sources/user-network-fs/libsmb2/examples/smb2-put-sync.c

Purpose: This synchronous example uploads a local file to an SMB path.

Important APIs and types: It uses POSIX `open`, `read`, `close`, libsmb2 `smb2_connect_share`, `smb2_open` with `O_WRONLY|O_CREAT`, `smb2_write`, `smb2_close`, and cleanup APIs.

Control flow: The program opens the local file, initializes SMB2, parses the destination URL from `argv[2]`, connects, opens/creates the remote path, reads local 1024-byte chunks, writes each chunk synchronously, then closes and disconnects.

State and persistence behavior: The persistent effect is writing remote file content. Local state is the input fd, static buffer, context, URL, and remote file handle.

Dependencies and integration points: It validates the blocking write wrapper and remote file creation path.

Risks: Argument validation checks only `< 2` despite requiring two arguments, so missing destination can access `argv[2]`. Return values from `smb2_write` are ignored, so short writes or errors during the loop are not detected. Existing remote files may not be truncated before overwrite.

Test signals: Compare remote file bytes with the local file, including files larger than one chunk, and test missing URL, permission denied, and existing larger destination files.
