# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_locku.c

Purpose: implements NFSv4 `LOCKU`, unlocking a byte range represented by a lock stateid.

Important APIs and types: uses `LOCKU4args/res`, `state_t`, `state_owner_t`, `fsal_obj_handle`, `fsal_lock_param_t`, and `state_status_t`. It calls `nfs4_check_stateid_acquire_state_lock`, `Check_nfs4_seqid_locked`, `state_unlock_locked`, `update_stateid_locked`, `Copy_nfs4_state_req`, and ref helpers.

Control flow: validates current regular file and lock type, builds an FSAL lock descriptor with unlock range, then validates the lock stateid while acquiring the state lock. NFSv4.0 requests check the lock owner seqid and may replay a cached response. It rejects stale owners, zero length, range overflow, and normalizes ranges past maxfilesize to EOF. With `op_ctx->clientid` set for v4.0, it calls `state_unlock_locked` under the state lock. Success updates the lock stateid into the response; v4.0 responses are cached in the lock owner for replay. The common cleanup unlocks state, drops owner/object/state refs, and traces result.

State and persistence: mutates SAL/FSAL byte-range lock state by removing all or part of a lock. It updates stateid sequencing/current stateid and v4.0 replay cache. It does not delete the lock stateid automatically unless lower SAL decides so.

Dependencies and integration: integrated with stateid validation, owner seqids, FSAL max file size, SAL unlock, and compound stateid propagation.

Risks: error paths after `nfs4_check_stateid_acquire_state_lock` must release state locks and refs exactly once. If `state_unlock_locked` partially succeeds then returns an error, protocol recovery depends on SAL behavior. As with LOCKT, maxfilesize subtraction needs valid starts.

Test signals: bad FH, invalid lock type, bad/replayed stateid, stale lock owner, v4.0 seqid replay, zero/overflow length, unlock full range, unlock partial range, maxfilesize normalization, and response cache behavior.
