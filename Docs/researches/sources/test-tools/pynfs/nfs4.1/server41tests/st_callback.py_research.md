# sources/test-tools/pynfs/nfs4.1/server41tests/st_callback.py

## Purpose
`st_callback.py` tests callback behavior around lock notification, specifically that expired clients do not receive `CB_NOTIFY_LOCK` while active waiters can.

## Important APIs, Types, and Functions
- `testCbNotifyLockExpiredClient` is the sole test. It installs callback hooks with `cb_pre_hook` and `cb_post_hook`, obtains conflicting locks, expires a client, and observes callback delivery.

## Control Flow
The test creates client/session pairs, has the first client take a write lock, has the second client fail a conflicting read lock with `NFS4ERR_DENIED`, keeps the first client alive while the second expires, forces server expiration with `env.serverhelper`, then closes the first lock and verifies no callback for the expired client. It then recreates the second client, repeats the conflict, closes the first lock, and expects `CB_NOTIFY_LOCK` so the second can retry the lock successfully.

## State and Persistence Behavior
The test manipulates open and byte-range lock state, client lease expiry, and callback hook state via `threading.Event`.

## Dependencies and Integration Points
It depends on environment file helpers, NFS lock owner types, `nfs_ops`, callback hook support in `nfs4client`, and an optional external server helper command capable of expiring a client.

## Risks and Edge Cases
The test uses fixed 60-second sleeps and an external expiration helper, so runtime and reliability depend on server lease settings and environment configuration. Courtesy-client behavior can affect intermediate expectations.

## Test Signals
Signals include `NFS4ERR_DENIED` for conflicting locks, no callback after forced expiry, `NFS4ERR_BADSESSION` for the expired session close, and callback delivery plus successful lock retry for the recreated active waiter.
