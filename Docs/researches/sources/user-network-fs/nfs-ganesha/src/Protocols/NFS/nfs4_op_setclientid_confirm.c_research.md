# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_setclientid_confirm.c

## Purpose
Implements NFSv4.0 SETCLIENTID_CONFIRM, promoting an unconfirmed clientid to confirmed state or updating an existing confirmed record after SETCLIENTID, with race handling, credential checks, callback testing, and old-client expiration.

## Important APIs, Types, and Functions
- `nfs4_op_setclientid_confirm` handles `NFS4_OP_SETCLIENTID_CONFIRM`.
- Uses `nfs_client_id_get_unconfirmed`, `nfs_client_id_get_confirmed`, `nfs_compare_clientcred`, `nfs_client_id_expire`, `remove_unconfirmed_client_id`, `nfs_client_id_confirm`, `nfs4_chk_clid`, `nfs_test_cb_chan`, `set_cb_chan_down`, and refcount helpers.
- `nfs4_op_setclientid_confirm_Free` is a no-op.

## Control Flow
The handler rejects minorversion greater than 0, first tries to find an unconfirmed clientid and otherwise a confirmed clientid, refs the client record, and locks it. For unconfirmed records it verifies principal/client address, treats already-confirmed matching records as successful races, and stale non-unconfirmed records as stale. For confirmed records it validates principal and verifier for idempotent retry or returns `CLID_INUSE`.

For a matching unconfirmed record, it fetches any current confirmed record. If the existing confirmed record has a different clientid, it expires it. If the same clientid is already confirmed, it updates callback fields and verifier from the unconfirmed record, removes the unconfirmed entry, refreshes the lease, and tests callback channel. Otherwise it confirms the new record, checks reclaim eligibility, tests callback channel, and returns OK.

## State and Persistence Behavior
Mutates clientid confirmation state, callback channel state, lease timestamps, expired-client lists, and potentially expires old client state. It removes unconfirmed records and may trigger recovery eligibility checks.

## Dependencies and Integration Points
Tightly coupled with SETCLIENTID, client manager tables, callback RPC channel creation/testing, NFSv4 recovery/reclaim code, credential matching, and delayed cleanup lists.

## Risks
Concurrency is the core risk: records may be confirmed or expired while this handler runs, so refcounts and record mutex ordering are critical. Principal mismatches must avoid hijacking live client state. Callback testing can mark channels down immediately after confirmation, influencing delegation behavior.

## Test Signals
Test confirming a new client, retrying confirm with same verifier, wrong verifier, confirmed-record retry, principal mismatch, stale clientid, old confirmed client expiration, update of same confirmed client callback data, callback up/down transitions, reclaim eligibility, and concurrent duplicate confirms.
