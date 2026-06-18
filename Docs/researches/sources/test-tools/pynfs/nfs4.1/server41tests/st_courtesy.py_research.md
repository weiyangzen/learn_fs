# sources/test-tools/pynfs/nfs4.1/server41tests/st_courtesy.py

## Purpose
`st_courtesy.py` tests NFSv4 courtesy-client behavior after lease expiry, with emphasis on locks, share reservations, conflicting opens, and purge performance.

## Important APIs, Types, and Functions
- `_getleasetime(sess)` reads `FATTR4_LEASE_TIME`.
- `cour_lockargs(fh, stateid)` builds a write lock operation sequence.
- Tests `testLockSleepLockU`, `testLockSleepLock`, `testShareReservation00`, `testShareReservationDB01`, `testShareReservationDB02`, `testShareReservationDB03`, and `testExpiringManyClients` cover courtesy lock/share scenarios.

## Control Flow
Tests create one or more client sessions, create/open files with selected access and deny modes, sleep beyond the lease period, and then verify whether conflicting locks or opens succeed. `testExpiringManyClients` creates many expired clients and measures whether a conflicting open can trigger purge without excessive delay.

## State and Persistence Behavior
The tests rely on server lease expiry, courtesy preservation of client state, open share reservations, and byte-range locks. State transitions are time-driven through sleeps of lease time plus a margin.

## Dependencies and Integration Points
The module depends on environment helpers for open/create/close, generated NFS lock and open types, and server support for courtesy-client semantics. It reads lease time through GETATTR.

## Risks and Edge Cases
These tests are slow and timing-sensitive. They assume lease expiry can be observed by sleeping and that servers distinguish expired courtesy state from active conflicts. The 1000-client test can be resource-intensive.

## Test Signals
Expected statuses include retained client operations succeeding or warning with `NFS4ERR_BADSESSION`, post-expiry conflicting locks/open succeeding, pre-expiry conflicts returning `NFS4ERR_SHARE_DENIED`, and large courtesy purges not blocking a valid conflicting open.
