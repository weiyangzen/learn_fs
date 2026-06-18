# sources/test-tools/pynfs/nfs4.1/server41tests/st_lookup.py

Purpose: basic NFSv4.1 `LOOKUP` behavior tests for home-path traversal and common error cases.

Important APIs/types/functions: active tests are `testHome`, `testNoFh`, `testNonExistent`, `testZeroLength`, and `testLongName`. The module also contains a large disabled `if 0` block with older object-type, access, invalid UTF-8, dot-name, and directory-permission lookup tests.

Control flow: each active test creates a client/session, composes NFS operations with `env.home`, `putrootfh`, `lookup`, and `getfh`, then validates the compound status. The disabled block follows the same pattern but uses legacy client helper methods.

State and persistence behavior: active tests do not create persistent state. They inspect namespace resolution against existing test roots and validate server error handling for missing current filehandle, nonexistent names, empty names, and overly long names.

Dependencies/integration: uses `NFS4ops`, constants from `xdrdef.nfs4_const`, and `server41tests.environment.check/fail`. It depends on `env.home` and server path options populated by the test harness.

Risks and test signals: coverage is currently narrow because many richer tests are disabled. The long-name case notes that `NOENT` might require checking `fattr4_maxname`, but the active assertion expects `NFS4ERR_NAMETOOLONG`.
