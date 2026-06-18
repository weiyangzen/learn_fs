# sources/test-tools/pynfs/nfs4.0/servertests/st_putfh.py

Purpose: Tests `PUTFH` by round-tripping filehandles for every standard object type, then checking bad and stale filehandle error handling.

Important APIs/types/functions: Uses `nfs_ops.NFS4ops`, `environment.check`, and helper `_try_put(t, c, path)`. Public tests cover file, symlink, block, char, directory, fifo, socket, `testBadHandle`, and `testStaleHandle`.

Control flow: `_try_put` looks up a path, obtains its handle with `GETFH`, then issues `PUTFH(oldfh), GETFH` and compares returned handles. Bad-handle tests feed `b'abc'`; stale-handle tests create, close, remove, and reuse an old handle.

State and persistence behavior: Mostly read-only except the stale-handle test, which creates and removes a file to invalidate a handle.

Dependencies and integration points: Relies on fixture paths and response-array access to `switch.switch.object`. Stale handling is marked ganesha-specific because servers may keep removed filehandles valid.

Risks: Stale filehandle behavior is not universally deterministic across servers/export implementations. The failure message joins byte paths using text `'/'.join(path)`, which may be fragile on Python 3 if reached.

Test signals: Checks success for valid handles, `NFS4ERR_BADHANDLE` for malformed handles, and `NFS4ERR_STALE` for removed handles in the optional stale test.
