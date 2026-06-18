# sources/user-network-fs/samba/source4/torture/smb2/maxwrite.c

## Purpose
`maxwrite.c` probes the maximum SMB2 write size accepted by a server and verifies data integrity for successful large writes.

## Important APIs, Types, and Functions
`torture_smb2_maxwrite()` establishes an SMB2 connection, creates `testmaxwrite.dat`, and delegates to `torture_smb2_write()`. `torture_smb2_write()` performs a binary search between one byte and 80,000,000 bytes using `smb2_write()` and `smb2_read()` on a single handle. It fills each candidate buffer with a deterministic byte pattern and compares the read-back buffer after successful writes.

## Control Flow
For each midpoint size, the helper allocates a temporary data blob, writes from offset zero, and either lowers `max` on failure or raises `min` on success. On write failure it closes and recreates the file handle; if close fails because the server disconnected, it reconnects and recreates. After every successful write it reads the same length from offset zero and checks length/content. When the search converges it closes and unlinks the test file.

## State and Persistence Behavior
The test repeatedly overwrites a single temporary file and removes it at the end. Local state is the binary-search bounds and the generated buffer for the current attempt. A server disconnect can replace the tree connection inside the helper.

## Dependencies and Integration Points
The code uses SMB2 create/read/write/close/unlink helpers and torture connection creation. It is an older stress-style test that exercises server max write request handling rather than a negotiated-size helper.

## Risks and Edge Cases
The helper always returns `NT_STATUS_OK` after convergence even if read-back mismatches were only logged, so integrity failures may not fail the test unless a status check fails. The local `tree` pointer is passed by value to the helper; reconnecting inside the helper does not update the caller, though the helper finishes cleanup itself. Large allocations and very large writes can be expensive.

## Test Signals
Signals include logged candidate sizes, write failure boundaries, reconnect handling after disconnect, read status, read length/content comparison, and the converged maximum size.
