# sources/test-tools/pynfs/nfs4.1/server41tests/st_putfh.py

Purpose: verifies `PUTFH` installs the exact current filehandle and rejects malformed filehandle bytes.

Important APIs/types/functions: `_try_put` and object-type tests `testFile`, `testLink`, `testBlock`, `testChar`, `testDir`, `testFifo`, `testSocket`, plus `testBadHandle`.

Control flow: `_try_put` looks up a configured object, obtains its handle with `GETFH`, issues `PUTFH` with that handle, then calls `GETFH` again and compares byte equality. `testBadHandle` sends `PUTFH(b'abc')` and expects `NFS4ERR_BADHANDLE`.

State and persistence behavior: read-only with respect to the server namespace. It depends on stable, reusable filehandles for existing test-tree objects.

Dependencies/integration: uses `use_obj`, `check`, `NFS4ops`, and configured option paths for every object kind.

Risks and test signals: object-kind tests require pre-existing test-tree entries. The test signal is direct filehandle equality, which is strong for `PUTFH`/`GETFH` but does not validate later operation behavior on the handle.
