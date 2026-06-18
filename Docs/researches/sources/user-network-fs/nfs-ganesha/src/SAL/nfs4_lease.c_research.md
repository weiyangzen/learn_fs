# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_lease.c

Purpose: Provides NFSv4 lease validation, reservation, renewal, and expiry handoff for `nfs_client_id_t` records.

Important APIs, types, and functions: `_valid_lease` computes remaining lifetime, `valid_lease` exposes the mutex-protected boolean check, `reserve_lease` increments `cid_lease_reservations`, `reserve_lease_or_expire` atomically reserves or forces client expiry, and `update_lease` drops a reservation and renews `cid_last_renew` when the last reservation exits.

Control flow: Lease validation returns invalid for `EXPIRED_CLIENT_ID`, valid for any active reservation, otherwise compares `cid_last_renew + lease_lifetime` against `time(NULL)`. A delayed-cleanup client is treated as still valid for non-reaper checks so active traffic can remove it from the expired list. `reserve_lease_or_expire` locks `cid_mutex`, reserves valid leases, optionally updates them, then asks the caller to unexpire outside the client mutex. If invalid, it takes temporary client/client-record refs, drops state-owner refs passed by the caller so expiry can clean owners, locks `cr_mutex`, calls `nfs_client_id_expire`, and releases all temporary refs.

State and persistence behavior: State is only the client record's `cid_last_renew`, `cid_lease_reservations`, confirmation state, and delayed-cleanup marker. Persistence is indirect: invalid lease handling invokes client expiry, which removes recovery records and state through other SAL files.

Dependencies and integration points: Uses global `nfs_param.nfsv4_param.lease_lifetime`, clientid refcount APIs, client-record refs, state-owner refs, delayed-expired-client list removal, and LTTng clientid tracepoints. It is called from stateid validation, reaper code, and NFSv4 operation processing paths that need to reserve a lease while mutating state.

Risks: Callers must hold `cid_mutex` for `valid_lease`, `reserve_lease`, and `update_lease` semantics; missing the required lock can corrupt reservation counts. Every successful reserve requires a later update/release path. The `st_owner` drop inside `reserve_lease_or_expire` is intentional to avoid owner cleanup deadlock; callers must tolerate it being nulled. Delayed-cleanup behavior makes lease validity context-sensitive via `is_from_reaper`.

Test signals: Cover lease lifetime boundary, reservation preventing expiry, last-reservation renewal, delayed-client validity from normal callers versus reaper, forced expiry on invalid lease, state-owner ref release during expiry, and list removal when renewed clients become active again.
