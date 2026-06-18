# sources/user-network-fs/samba/source3/include/client.h

## Purpose
`client.h` defines central source3 SMB client structures, print job metadata, directory/file info records, client timeout/buffer constants, and full-connection option flags.

## Important APIs, Types, And Functions
- `CLI_BUFFER_SIZE` aliases maximum SMB buffer size; `CLIENT_TIMEOUT` defaults to 20 seconds.
- `struct print_job_info` stores print job id, priority, size, user, name, and time.
- `struct cli_state` represents an SMB client connection, including DFS linked-list pointers, error mapping, server strings, share/device, timeout, POSIX capabilities, pipe list, oplock preference, low-level connection pointer, and SMB1/SMB2 session/tree state.
- `struct file_info` is a directory listing/stat result with size, allocation, attributes, inode, timestamps, name/short name, reparse tag, POSIX stat fields, owner/group SIDs, and POSIX flag.
- `CLI_FULL_CONNECTION_*` flags control SPNEGO, anonymous fallback, oplocks, DOS errors, ASCII, SMB1 forcing/disabling, IPC, and POSIX requests.

## Control Flow
This is a data contract header. Client connection functions populate and mutate `cli_state`; listing/stat functions populate `file_info`; higher-level tools such as `clitar.c` consume these fields to transfer files.

## State And Persistence
`cli_state` is live connection state and owns active sessions/tree connects/open handles indirectly. It is not persistent, but it gates network resources. `file_info` is snapshot metadata returned from remote servers.

## Dependencies And Integration Points
It integrates source3 client code with SMBXCLI, RPC pipe clients, IDR open handle tracking, Samba fixed string types, SID types, and DOS/SMB constants.

## Risks
Fields span SMB1 and SMB2 and must be interpreted according to negotiated dialect. Direct field access by many modules makes refactoring risky. Timeout and flag defaults influence many command-line tools.

## Test Signals
Test full connection options across SMB1/SMB2, DFS subsidiary connections, POSIX capability negotiation, file_info population for normal and POSIX listings, reparse tags, owner/group SIDs, and print job metadata.
