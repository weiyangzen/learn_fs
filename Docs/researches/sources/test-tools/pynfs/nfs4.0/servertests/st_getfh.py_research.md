# sources/test-tools/pynfs/nfs4.0/servertests/st_getfh.py

## Purpose
`st_getfh.py` tests the NFSv4 `GETFH` operation for all standard test-tree object types and the no-current-filehandle error path.

## Important APIs, Types, And Functions
- `testFile`, `testDir`, `testLink`, `testSocket`, `testFifo`, `testBlock`, and `testChar` call `env.c1.do_getfh` on environment paths.
- `testNoFh(t, env)` sends raw `GETFH` without establishing current filehandle and expects `NFS4ERR_NOFILEHANDLE`.

## Control Flow
Object tests delegate entirely to the client helper, which performs the LOOKUP/use-object and GETFH sequence. The no-fh test constructs a compound with only `op.getfh()` and checks the status.

## State And Persistence Behavior
No persistent state is created. On the local Python server, GETFH also populates the server's in-memory filehandle cache, which may influence later PUTFH behavior outside this module.

## Dependencies And Integration Points
Imports include NFS constants, `check`, and `nfs_ops`. It depends on `Environment._maketree` object paths and `NFS4Client.do_getfh`.

## Risks And Edge Cases
- `testFifo` appears to call `do_getfh(env.opts.uselink)` rather than `env.opts.usefifo`, likely reducing FIFO coverage.
- The helper abstracts away response content, so these tests mainly validate status and decoding rather than uniqueness or volatility properties.

## Test Signals
Signals are successful GETFH on each object type and `NFS4ERR_NOFILEHANDLE` for a missing current filehandle.
