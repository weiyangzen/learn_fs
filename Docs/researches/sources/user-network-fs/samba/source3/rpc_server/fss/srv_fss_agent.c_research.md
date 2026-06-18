# sources/user-network-fs/samba/source3/rpc_server/fss/srv_fss_agent.c

Purpose: File Server Remote VSS Protocol server implementation that coordinates shadow copy set lifecycle, snapshot creation/deletion through VFS hooks, exposed snapshot shares, state persistence, access checks, and sequence timers.

Important APIs/types/functions: `fss_global`, `fss_ntstatus_map`, `fss_unc_parse`, `fss_prune_stale`, `srv_fssa_start`, `fss_permitted`, `fss_seq_tout_set`, `_fss_SetContext`, `_fss_StartShadowCopySet`, `_fss_AddToShadowCopySet`, `_fss_PrepareShadowCopySet`, `_fss_CommitShadowCopySet`, `_fss_ExposeShadowCopySet`, `_fss_RecoveryCompleteShadowCopySet`, `_fss_AbortShadowCopySet`, `_fss_IsPathSupported`, `_fss_GetShareMapping`, `_fss_DeleteShareMapping`, and `sc_smap_unexpose`.

Control flow: clients must set a context, start a set, add one or more shares, optionally prepare, commit snapshots through `SMB_VFS_SNAP_CREATE`, expose committed snapshots by cloning share definitions into registry smbconf, query mappings, complete recovery, and later delete mappings. A single in-progress set is enforced. Timers clear unfinished state after message-sequence timeouts; successful operations restart timers with protocol-specific intervals.

State/persistence behavior: active state lives in `fss_global` and nested `fss_sc_set`/`fss_sc`/`fss_sc_smap` lists. Committed/exposed/recovered state is stored in `srv_fss.tdb` through `fss_state_store`. Exposed shares are persistent registry smbconf entries; snapshot paths are owned by the underlying VFS module. Optional startup pruning removes state and shares for missing snapshot paths.

Dependencies/integration: integrates Samba authorization tokens, Backup Operators/Administrators checks, VFS snapshot hooks, smbconf registry/file backends, share security cloning, global messaging for config updates and forced tree disconnects, generated FSRVP NDR, and private state helpers.

Risks/test signals: error mapping must match FSRVP/HRESULT expectations. Share parsing accepts UNC paths and truncates trailing path components. Registry transactions guard expose/unexpose, but share security cloning is outside that transaction. Tests should cover permission gates, illegal state transitions, timer cleanup, duplicate volume handling, snapshot VFS failures, expose rollback, persisted restart recovery, stale pruning, and delete behavior when multiple share mappings refer to one snapshot.
