# sources/test-tools/pynfs/nfs4.1/server41tests/st_sparse.py

Purpose: NFSv4.2 sparse-file `ALLOCATE` smoke tests with open, all-zero, and all-one stateids.

Important APIs/types/functions: `testAllocateSupported`, `testAllocateStateidZero`, and `testAllocateStateidOne`.

Control flow: each test creates a write-open file, extracts its filehandle and sometimes open stateid, then issues `ALLOCATE` for offset `0`, length `1` with the selected stateid and checks success.

State and persistence behavior: creates files and asks the server to reserve or allocate one byte of backing storage. The operation may change file allocation metadata without changing visible data.

Dependencies/integration: requires minor version 2 or later (`VERS: 2-`), `create_file`, environment special stateids `stateid0`/`stateid1`, and `NFS4ops.allocate`.

Risks and test signals: no readback or allocation attribute verification is performed. The suite only verifies that the server accepts the requests.
