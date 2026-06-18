# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_downgrade.c

Purpose: implements `OPEN_DOWNGRADE`, reducing the share access/deny mode associated with an open stateid.

Important APIs and types: uses `OPEN_DOWNGRADE4args/res`, `state_t`, `state_owner_t`, `fsal_obj_handle`, and `fsal_openflags_t`. Key helpers are `share_downgrade_allowed` and `nfs4_do_open_downgrade_locked`, plus stateid/seqid APIs `nfs4_check_stateid_acquire_state_lock`, `Check_nfs4_seqid_locked`, `update_stateid_locked`, and `Copy_nfs4_state_req`.

Control flow: validates the current FH and requires a regular file. It validates the open stateid while acquiring the state lock, checks v4.0 seqid if needed, then calls `nfs4_do_open_downgrade_locked`. The helper verifies the requested share access and deny are subsets of current state. It also verifies the target mode was previously seen using `share_access_prev`/`share_deny_prev`; special handling allows target BOTH when READ and WRITE were separately seen. It converts target share bits into FSAL open flags and calls `fsal_reopen2(..., true)`. Success updates the open stateid and caches v4.0 response.

State and persistence: changes FSAL open/share reservation mode for an existing share state, updates stateid sequencing/current stateid, and uses replay cache. It does not directly edit the in-memory `share_access`/`share_deny` fields in the helper visible here; it relies on `fsal_reopen2`/state integration for effective downgrade behavior.

Dependencies and integration: depends on share history encoded during `OPEN`, FSAL reopen semantics, SAL stateid validation, v4.0 seqid replay, and export state locks.

Risks: if `fsal_reopen2` does not update SAL share fields, the in-memory state may remain broader than intended. The bit-history encoding uses `(1 << mode)` where `mode` can itself be a bitmask; tests must preserve this convention. Error logging uses a cause pointer to aid diagnosis.

Test signals: bad/non-regular FH, bad/replayed stateid, stale state, invalid subset access/deny, target share mode never previously opened, BOTH allowed from separate read/write opens, FSAL reopen failure, successful stateid update, and v4.0 response replay.
