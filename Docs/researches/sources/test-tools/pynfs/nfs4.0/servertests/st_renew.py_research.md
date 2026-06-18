# sources/test-tools/pynfs/nfs4.0/servertests/st_renew.py

Purpose: Tests NFSv4 `RENEW` for a valid clientid, a stale/bad clientid, and an expired lease.

Important APIs/types/functions: Imports `nfs_ops.NFS4ops.renew` and `environment.check`; exposes `testRenew`, `testBadRenew`, and `testExpired`.

Control flow: `testRenew` initializes a client and renews its `clientid`. `testBadRenew` renews clientid `0`. `testExpired` creates deny state, sleeps for twice the lease time, lets another client open the file, then renews with the original client.

State and persistence behavior: Mutates and observes client lease state. The expired test intentionally lets a lease lapse and introduces another client to force conflict/state expiration.

Dependencies and integration points: Uses lease time from the client wrapper, two environment clients, and open/share deny state.

Risks: Timing-sensitive and can be affected by server grace/lease implementation. Sleeping twice the lease time may slow runs.

Test signals: Expects success for valid renew, `NFS4ERR_STALE_CLIENTID` for bad clientid, and `NFS4ERR_EXPIRED` after lease expiry.
