# sources/user-network-fs/samba/source4/torture/smb2/maxfid.c

## Purpose
`maxfid.c` stress-tests how many SMB2 file identifiers/open handles a server and client test environment can sustain on one tree connection.

## Important APIs, Types, and Functions
The sole exported test function is `torture_smb2_maxfid()`. It reads the `maxopenfiles` torture setting, defaults to `65520`, opens an SMB2 connection, allocates an array of `struct smb2_handle`, creates a directory fanout under `smb2_maxfid`, then opens files until the requested limit is reached or the server returns an error.

## Control Flow
After connecting and creating the base directory, the test creates one subdirectory per 1000 intended files to avoid a single huge directory. It then loops from zero to `max_handles - 1`, creates `smb2_maxfid\\<bucket>\\<i>`, stores each returned handle, and stops on first create failure. It reports whether the configured limit was reached, closes every successfully opened handle, and removes the tree.

## State and Persistence Behavior
The server accumulates many live file handles and created test files during the run. Local state is the handle array and the `maxfid` count. Cleanup closes only handles that were actually opened and then deletes the base directory tree.

## Dependencies and Integration Points
The file uses `torture_smb2_connection()`, SMB2 create/close helpers, `torture_smb2_testdir()`, `smb2_deltree()`, and the `maxopenfiles` setting. The source comment notes socket-wrapper limits and `SOCKET_WRAPPER_MAX_SOCKETS` for larger local test runs.

## Risks and Edge Cases
This is intentionally resource-heavy. Memory allocation, server open-file limits, client socket-wrapper limits, share quotas, and filesystem directory scaling can all terminate the loop before the configured maximum. On early failure, cleanup still depends on closing all stored handles and deleting a potentially large tree.

## Test Signals
Primary signals are the number of successful opens before failure, the exact create error at the limit, successful cleanup closes, and whether the configured `maxopenfiles` ceiling was reached.
