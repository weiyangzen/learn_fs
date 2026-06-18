# sources/test-tools/pynfs/nfs4.0/servertests/st_locku.py

Purpose: Exercises NFSv4 `LOCKU` unlock behavior for regular files, partial ranges, invalid ranges, sequence-id handling, bad/stale/old lock stateids, and lease-expired unlock attempts.

Important APIs/types/functions: Imports `NFS4ERR_*` constants, `stateid4`, and `environment.check/makeStaleId`. Test entry points are `testFile`, `testUnlocked`, `testSplit`, `testOverlap`, `test32bitRange`, `testZeroLen`, `testLenTooLong`, `testNoFh`, `testBadLockSeqid*`, `testOldLockStateid`, `testBadLockStateid`, `testStaleLockStateid`, and `testTimedoutUnlock`. They use client helpers `init_connection`, `create_confirm`, `lock_file`, `relock_file`, `unlock_file`, `lock_test`, `getLeaseTime`, and `env.sleep`.

Control flow: Each test creates or opens a file, obtains a lock owner/stateid through `lock_file`, performs one unlock operation, and checks either success or a precise protocol error. Range tests vary offset/length; sequence tests deliberately reuse or skip lockseqid values; timeout tests sleep past the lease before unlocking.

State and persistence behavior: Mutates server lock state and open state under `env.c1`, with lease expiration as a persistent server-side state transition. Lock-owner sequenceids and lock stateids are the main state under test.

Dependencies and integration points: Depends on pynfs server-test environment, NFSv4 XDR constants, and a server that supports byte-range locks. Some tests depend on previous `MKFILE`, `LOCK*`, or timed/ganesha-specific flags from docstrings.

Risks: Timing-sensitive lease tests can be flaky if server lease reporting or sleep scheduling is imprecise. Some servers legitimately return `NFS4ERR_LOCK_RANGE` for non-matching unlocks; the tests distinguish support warnings from hard failures. Bad replay semantics are noted in comments for one sequence-id case.

Test signals: `check()` validates `NFS4_OK`, `NFS4ERR_DENIED`, `NFS4ERR_LOCK_RANGE`, `NFS4ERR_BAD_RANGE`, `NFS4ERR_INVAL`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_SEQID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, and `NFS4ERR_EXPIRED`; `t.fail`/`t.fail_support` mark stricter conformance expectations.
