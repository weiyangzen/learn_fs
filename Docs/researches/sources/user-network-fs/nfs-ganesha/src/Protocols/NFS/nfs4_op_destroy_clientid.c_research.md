# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_destroy_clientid.c

Purpose: implements `NFS4_OP_DESTROY_CLIENTID` for NFSv4.1+ by removing confirmed and/or unconfirmed clientid records when they are no longer active. The handler is centered on `nfs4_op_destroy_clientid`, with `nfs4_op_destroy_clientid_Free` as a no-op result cleanup hook.

Important APIs and types: it consumes `DESTROY_CLIENTID4args` and fills `DESTROY_CLIENTID4res`, uses SAL client identity types `nfs_client_record_t` and `nfs_client_id_t`, and coordinates with `nfs_client_id_get_confirmed`, `nfs_client_id_get_unconfirmed`, `remove_confirmed_client_id`, `remove_unconfirmed_client_id`, `nfs4_rm_clid`, and reference helpers. It also uses `cr_mutex` and `cid_mutex` for record-level and clientid-level synchronization.

Control flow: the operation sets `resp->resop`, traces the request, looks first for a confirmed clientid, falls back to unconfirmed, then rechecks confirmed to handle a race where another thread confirmed the clientid during lookup. If nothing is found it returns `NFS4ERR_STALE_CLIENTID`. Once a record is found, it increments the client record ref, locks `client_record->cr_mutex`, re-reads the confirmed/unconfirmed pointers, and exits quietly if another destroy already removed both. Confirmed records are not removed if their NFSv4.1 callback session list is non-empty, returning `NFS4ERR_CLIENTID_BUSY`. Otherwise the confirmed stable-storage record is removed through `nfs4_rm_clid` and the record is unhashed. Unconfirmed records are unhashed similarly.

State and persistence: this file directly mutates SAL clientid tables and removes the stable clientid record for confirmed clients. It depends on reference counts and mutex ordering to avoid use-after-free while racing EXCHANGE_ID, CREATE_SESSION, and other destroy paths.

Dependencies and integration: integrates with NFS compound dispatch, SAL clientid management, LTTng tracepoints, and logging. The returned status is converted through `nfsstat4_to_nfs_req_result`.

Risks: races around confirmed/unconfirmed transitions are the main risk; the double lookup and recheck under `cr_mutex` are essential. Session checks rely on `cid_cb.v41.cb_session_list` as the proxy for "busy"; future state forms would need matching checks. Stable-storage removal before unhashing must remain ordered carefully.

Test signals: cover stale clientids, destroying only-unconfirmed records, destroying confirmed records with no sessions, `NFS4ERR_CLIENTID_BUSY` when sessions exist, and concurrent confirm/destroy races. Lease recovery tests should verify stable clientid records disappear after successful destroy.
