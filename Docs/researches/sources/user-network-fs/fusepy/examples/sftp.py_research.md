# sources/user-network-fs/fusepy/examples/sftp.py

## Purpose
`sftp.py` is a fusepy example that exposes a remote SFTP server as a FUSE filesystem through Paramiko. It forwards common file and directory operations to `paramiko.SFTPClient`.

## Important APIs, Types, and Functions
- `SFTP(LoggingMixIn, Operations)`: opens SSH/SFTP connections in `__init__`.
- Connection lifecycle: `__init__(host, username=None, port=22)` and `destroy()`.
- Metadata/namespace operations: `getattr`, `chmod`, `chown`, `mkdir`, `rename`, `rmdir`, `symlink`, `readlink`, `truncate`, `unlink`, `utimens`.
- Data operations: `create`, `read`, `write`.

## Control Flow
Main parses optional `-l`, host, and mount. If login is not provided and host contains `user@host`, it splits that into username and host. The filesystem connects using system host keys plus `AutoAddPolicy`, opens SFTP, and mounts foreground with `nothreads=True` and `allow_other=True`. Each read/write opens a remote file, seeks, transfers data, and closes it.

## State and Persistence
Persistent state is entirely remote SFTP server state. Local in-memory state is the SSH client and SFTP client. Changes to remote files, directories, links, modes, owners, and timestamps are immediate server operations.

## Dependencies and Integration Points
It depends on Paramiko for SSH/SFTP and fusepy for mounting. It integrates with SSH host-key files, authentication agents/keys, network connectivity, and remote server permissions.

## Risks and Edge Cases
`AutoAddPolicy` trusts unknown host keys, which is convenient but weakens host authenticity. The example assumes passwordless/key-based login. Each read/write opens and closes a remote file, which is simple but slow. `readdir()` returns encoded byte names while many fusepy examples return strings; this can interact with encoding expectations. `create()` returns `0` instead of a distinct file handle. `nothreads=True` avoids concurrency issues but limits parallelism.

## Test Signals
Test against a disposable SFTP server: mount, list directories, stat files, create/write/read/truncate/rename/unlink, symlink/readlink, chmod/chown if permitted, and connection teardown on unmount. Include host-key behavior and login parsing tests.
