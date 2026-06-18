# sources/test-tools/pynfs/nfs4.1/server41tests/st_exchange_id.py

## Purpose
`st_exchange_id.py` tests NFSv4.1 `EXCHANGE_ID` behavior, including basic support, pNFS flag reporting, SSV setup, implementation id encoding, invalid flags, confirmed/unconfirmed client-owner replacement cases, update semantics, not-only-op rules, and lease expiry of unconfirmed records.

## Important APIs, Types, and Functions
- `_getleasetime(sess)` reads the server lease time.
- `_raw_exchange_id(c, name, verf=None, cred=None, protect=None, flags=0)` sends a configurable `EXCHANGE_ID`.
- `testSupported`, `testSupported1a`, `testSupported2`, `testSSV`, `testNoImplId`, `testLongArray`, and `testBadFlags` cover basic protocol validation.
- `testNoUpdate*` and `testUpdate*` encode draft-21 client-owner case matrix tests.
- `testNotOnlyOp` and `testLeasePeriod` cover operation placement and unconfirmed record expiry.

## Control Flow
Tests construct `client_owner4` values from verifier/name pairs, choose state protection, send `op.exchange_id`, and inspect returned status, clientid, flags, and later session behavior. Matrix tests vary confirmed state, verifier equality, principal equality, and update flag presence.

## State and Persistence Behavior
The tests exercise server client-owner records, unconfirmed vs confirmed clientids, verifier-based reboot detection, principal ownership, session invalidation after replacement, and lease-driven expiry of unconfirmed records.

## Dependencies and Integration Points
The module depends on environment assertions and verifier generation, generated NFS types/constants, `nfs_ops`, `nfs4lib` hash/encryption OID registries, RPC exceptions, and real credentials from the test environment.

## Risks and Edge Cases
There are two functions named `testSupported1a`; the latter server-only-flag test overwrites the earlier simple-flag test in normal Python module loading. Several tests are draft-21 specific and may differ from final RFC behavior or server policy. Lease tests use sleeps and can be slow or flaky when lease times are large or cleanup policies vary.

## Test Signals
Expected signals include `NFS4_OK`, server pNFS/non-pNFS use flags set in `eir_flags`, `NFS4ERR_BADXDR` or RPC `GARBAGE_ARGS` for too-long implementation arrays, `NFS4ERR_INVAL` for bad/server-only flags, `NFS4ERR_NOENT`, `NFS4ERR_NOT_SAME`, `NFS4ERR_PERM`, `NFS4ERR_CLID_INUSE`, `NFS4ERR_STALE_CLIENTID`, and `NFS4ERR_NOT_ONLY_OP`.
