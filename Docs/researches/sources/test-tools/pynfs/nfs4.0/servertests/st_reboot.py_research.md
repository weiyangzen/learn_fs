# sources/test-tools/pynfs/nfs4.0/servertests/st_reboot.py

Purpose: Optional, non-default NFSv4.0 server reboot/grace-period suite covering `CLAIM_PREVIOUS`, stale clientids after reboot, multiple clients, late reclaims, RFC edge cases for lock reclaim, root-squash preservation, delegation reclaim, repeated reboots, and grace-period seqid handling.

Important APIs/types/functions: `_waitForReboot` reads lease time, calls `env.serverhelper(b"reboot")`, waits with `c.null()`, and returns an estimated grace wait. Public tests include `testRebootValid`, `testManyClaims`, `testRebootWait`, `testEdge1`, `testEdge2`, `testRootSquash`, `testValidDeleg`, `testRebootMultiple`, and `testGraceSeqid`.

Control flow: Tests create confirmed opens or locks, reboot the server through the environment helper, then try `OPEN` with `CLAIM_PREVIOUS` before/during/after grace. `finally` blocks sleep until grace ends to avoid poisoning later tests.

State and persistence behavior: Intentionally destroys and reclaims server state across reboot. It relies on persistent filehandles/files surviving reboot and server lock/clientid databases being reset according to the protocol.

Dependencies and integration points: Requires configured `serverhelper`, real server reboot support, lease time reporting, optional delegation helper from `st_delegation`, AUTH_SYS root setup for root-squash testing, and multiple clients.

Risks: Highly timing- and environment-sensitive. It can disrupt other tests and is not part of the standard suite. Incorrect grace cleanup can leave the server in a transient state for subsequent tests.

Test signals: Checks `NFS4_OK`, `NFS4ERR_STALE_CLIENTID`, `NFS4ERR_NO_GRACE`, `NFS4ERR_RECLAIM_BAD`, and `NFS4ERR_GRACE`, plus owner/delegation comparisons and support failures when prerequisites are missing.
