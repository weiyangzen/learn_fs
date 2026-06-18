# sources/test-tools/pynfs/nfs4.0/servertests/st_opendowngrade.py

Purpose: Validates `OPENDOWNGRADE` for regular files, invalid downgrades to unopened access modes, bad seqids/stateids, stale/old stateids, missing current filehandle, complex upgrade/downgrade sequences, and interaction with locks.

Important APIs/types/functions: Imports constants and `makeStaleId`. Public tests include `testRegularOpen`, `testNewState1`, `testNewState2`, `testBadSeqid`, `testBadStateid`, `testStaleStateid`, `testOldStateid`, `testNoFh`, `testOpenDowngradeSequence`, and `testOpenDowngradeLock`. The local `open_sequence` class wraps `open`, `downgrade`, `close`, and `lock` state transitions.

Control flow: Basic cases create/open a file, call `downgrade_file`, and assert status. Sequence tests repeatedly open with READ/WRITE/BOTH access, downgrade to narrower access, and close. Lock interaction opens, locks with `READ_LT`, downgrades, then closes.

State and persistence behavior: Mutates open-owner seqids, open share access, stateids, and optionally lock state. `open_sequence.downgrade` updates its stored stateid from the response.

Dependencies and integration points: Uses pynfs client open/downgrade wrappers and NFSv4 share access constants. Tests depend on normal `MKFILE` setup and lock support.

Risks: The helper does not check every intermediate result explicitly in complex sequences, so exceptions or wrapper assertions are the primary failure signal there. Sequence-id behavior depends on client wrapper tracking.

Test signals: Expected statuses include `NFS4_OK`, `NFS4ERR_INVAL`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_OLD_STATEID`, and `NFS4ERR_NOFILEHANDLE`.
