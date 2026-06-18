# sources/test-tools/pynfs/nfs4.0/servertests/st_read.py

Purpose: Tests NFSv4 `READ` semantics for normal reads, stateid zero/one/open-stateid, large counts and offsets, zero count, non-file objects, missing filehandles, bad/stale/old stateids, stolen stateids, and multi-read large-data behavior.

Important APIs/types/functions: Imports `check`, `makeBadID`, `makeBadIDganesha`, `makeStaleId`, and `rpc.rpc`. `_compare` validates returned data prefix and EOF behavior. Public tests include `testSimpleRead`, `testStateidOnes`, `testWithOpen`, `testLargeCount`, `testLargeOffset`, `testVeryLargeOffset`, `testZeroCount`, object-type failures, `testBadStateidGanesha`, `testStaleStateid`, `testOldStateid`, `testStolenStateid`, and `testLargeMultipleRead`.

Control flow: Tests call `c.read_file` on fixture paths or freshly created filehandles, then `_compare` the returned bytes and EOF flag. Stateid tests create/confirm opens and mutate or reuse stateids.

State and persistence behavior: Mostly read-only, with setup creating sparse or zero-filled files and changing client security temporarily for stolen-stateid coverage.

Dependencies and integration points: Relies on `env.filedata`, fixture object paths, client helpers for open/confirm, and AUTH_SYS credential manipulation.

Risks: Large read tests can stress memory and server transfer limits. EOF expectations and symlink/non-file status alternatives vary by server.

Test signals: Checks `NFS4_OK`, `NFS4ERR_ISDIR`, `NFS4ERR_INVAL`, `NFS4ERR_SYMLINK`, `NFS4ERR_NOFILEHANDLE`, `NFS4ERR_BAD_STATEID`, `NFS4ERR_STALE_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_ACCESS`, and `NFS4ERR_PERM`, plus direct byte/EOF failures from `_compare`.
