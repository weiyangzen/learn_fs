# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_lockt.c

Purpose: implements NFSv4 `LOCKT`, a test-only byte-range lock request that reports whether a lock would conflict.

Important APIs and types: uses `LOCKT4args/res`, `state_owner_t`, `nfs_client_id_t`, `state_t`, and `fsal_lock_param_t`. Calls include `nfs4_sanity_check_FH`, `nfs_get_grace_status`, `nfs_client_id_get_confirmed`, `reserve_lease_or_expire`, `convert_nfs4_lock_owner`, `create_nfs4_owner`, `nfs4_State_Get_Obj`, `state_test`, `Process_nfs4_conflict`, and `Release_nfs4_denied`.

Control flow: validates current regular file, rejects zero length, and rejects non-reclaim activity during grace. It maps read/write lock type to FSAL lock type, rejects invalid types, normalizes EOF length to zero, checks overflow and maxfilesize. It resolves the clientid from the request for v4.0 or session for v4.1, reserves the v4.0 lease, creates/fetches a lock owner, and for v4.0 sets `op_ctx->clientid`. It optionally retrieves an existing lock state for this object/owner, locks the object state, and calls `state_test`. Conflicts are encoded into `LOCK4denied`; non-conflict statuses are converted from SAL state status.

State and persistence: should not create persistent locks, but it may create a lock owner record as part of owner resolution. It updates the v4.0 lease on exit and releases grace status.

Dependencies and integration: depends on NFS grace coordination, SAL lock conflict testing, clientid/owner management, FSAL max file size, and denied response allocation/free helpers.

Risks: creating a lock owner for a test request may leave owner state behind depending on owner cache behavior. `nfs_put_grace_status` is called unconditionally at `out`, but `nfs_get_grace_status(false)` only succeeds on the main path; the grace helper must tolerate this pairing. Maxfilesize subtraction assumes `lock_start <= maxfilesize`.

Test signals: valid read/write tests, invalid type, zero length, overflow length, past-maxfilesize range, grace rejection, unknown clientid, conflict denied content and cleanup, and no-conflict success.
