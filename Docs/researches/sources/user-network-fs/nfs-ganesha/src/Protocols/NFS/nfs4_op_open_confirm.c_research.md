# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_open_confirm.c

Purpose: implements NFSv4.0 `OPEN_CONFIRM`, confirming an open owner that previously required confirmation. NFSv4.1+ does not support this operation.

Important APIs and types: uses `OPEN_CONFIRM4args/res`, `OPEN_CONFIRM4resok`, `state_t`, `state_owner_t`, and `fsal_obj_handle`. It calls `nfs4_sanity_check_FH`, `nfs4_check_stateid_acquire_state_lock`, `Check_nfs4_seqid_locked`, `update_stateid_locked`, `Copy_nfs4_state_req`, and ref helpers.

Control flow: minorversion greater than zero returns `NFS4ERR_NOTSUPP`. The current FH must be a regular file. The supplied open stateid is validated while acquiring the state lock. Replay (`NFS4ERR_REPLAY`) is allowed through to seqid handling. The open owner must still exist; otherwise stale state returns `NFS4ERR_STALE`. Under owner mutex the v4.0 seqid is checked. If the owner is already confirmed, the operation returns `NFS4ERR_BAD_STATEID`. Otherwise it marks `so_confirmed = true`, updates the stateid under lock, and saves the response in the open owner replay cache.

State and persistence: mutates the open owner's confirmed flag, updates stateid sequencing/current stateid, and records the response for NFSv4.0 replay. It does not change FSAL open state.

Dependencies and integration: coupled to `OPEN` result flag `OPEN4_RESULT_CONFIRM`, owner replay cache, SAL stateid validation, and compound stateid propagation.

Risks: replay handling depends on `nfs4_check_stateid_acquire_state_lock` and `Check_nfs4_seqid_locked` cooperating while the response union is prefilled. Already-confirmed state must not accidentally advance seqids. Lock/ref cleanup is important on early stale paths.

Test signals: v4.1 not supported, non-regular FH, bad stateid, stale owner, seqid replay, already-confirmed owner, successful confirmation and replayed confirmation response.
