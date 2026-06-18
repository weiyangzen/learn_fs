# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_free_stateid.c

Purpose: implements NFSv4.1 `FREE_STATEID`, allowing clients to free stateids, especially lock stateids with no held locks and revoked delegation stateids.

Important APIs and types: uses `FREE_STATEID4args`, `FREE_STATEID4res`, `state_t`, `fsal_obj_handle`, and `gsh_export`. It calls `is_stateid_revoked`, `atomic_remove_revoked_and_clear_flags`, `nfs4_Check_Stateid`, `get_state_obj_export_owner_refs`, `save_op_context_export_and_set_export`, `state_del_locked`, and state/object/export reference helpers.

Control flow: minorversion 0 is rejected with `NFS4ERR_INVAL`. Revoked delegation stateids are special-cased before normal stateid validation: if the stateid is on the revoked list it is atomically removed and client session flags may be cleared; the operation returns `NFS4_OK`. For normal stateids, `nfs4_Check_Stateid` resolves the state using `STATEID_SPECIAL_CURRENT`. The handler obtains object/export refs, switches `op_ctx` to the state export, locks the object state, and only frees `STATE_TYPE_LOCK` stateids whose lock list is empty. Any other state or lock state with held locks returns `NFS4ERR_LOCKS_HELD`.

State and persistence: mutates revoked delegation bookkeeping and may delete a lock state from SAL state tables. It preserves export context while manipulating state, then restores it. It does not directly change stable storage.

Dependencies and integration: integrated with NFSv4.1 sessions for revoked delegation notification flags, SAL state validation/deletion, FSAL object references, export context switching, and LTTng.

Risks: the code explicitly supports only empty lock stateids; future support for other state types would need additional protocol checks. The revoked path assumes `data->session` is present for v4.1; logging dereferences `clientid` in one branch after the atomic helper succeeds, so tests should include session-present assumptions. Locking object state before `state_del_locked` is required.

Test signals: revoked delegation cleanup, revoked cleanup when more revoked delegations remain, invalid stateid, empty lock state deletion, lock state with held locks returning `LOCKS_HELD`, and non-lock state rejection.
