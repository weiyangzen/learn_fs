# sources/test-tools/pynfs/nfs4.1/server41tests/st_open.py

Purpose: NFSv4.1 `OPEN`, open stateid sequencing, simple read/write through open state, anonymous stateid I/O, exclusive create verifier behavior, `CLAIM_FH`, and close-with-zero-seqid tests.

Important APIs/types/functions: `expect`, `testSupported`, `testServerStateSeqid`, `testReadWrite`, `testAnonReadWrite`, `testEXCLUSIVE4AtNameAttribute`, `testOPENClaimFH`, and `testCloseWithZeroSeqid`. It imports open-owner, open-flag, claim, stateid, and lock-owner XDR types, though not all are used.

Control flow: tests create sessions, create/open files via environment helpers, assert returned open stateid `seqid` values, write data at offset 5, read it back, and close. `testOPENClaimFH` closes the initial open, then reopens by current filehandle with `CLAIM_FH`.

State and persistence behavior: creates files in the test directory and writes data containing a hole prefix. The server's open-owner state and stateid sequencing are the main state under test. Some tests set `stateid.seqid = 0` to verify special current-state semantics accepted by read/write/close paths.

Dependencies/integration: uses `st_create_session`, `server41tests.environment` file helpers, `nfs_ops`, `nfs4lib.state00`, and NFSv4.1 generated constants/types.

Risks and test signals: the helper `expect` assumes the open result is at `resarray[-2]`, so compound shape changes would break it. The tests do not deeply inspect delegations, and several imported lock-related types are unused.
