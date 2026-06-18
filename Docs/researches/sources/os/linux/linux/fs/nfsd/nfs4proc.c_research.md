# File Research: sources/os/linux/linux/fs/nfsd/nfs4proc.c

This file is the main NFSv4 server procedure dispatcher and operation implementation table for NFSD. It handles NFSv4 COMPOUND execution, filehandle operations, create/open/read/write metadata operations, server-side copy/offload, pNFS operation glue, xattrs, reply size estimation, operation ordering rules, and the exported NFSv4 `svc_version`.

Primary responsibilities:
- Implement many NFSv4 operation handlers used by the operation table.
- Enforce NFSv4.0/NFSv4.1 COMPOUND ordering and filehandle rules.
- Manage current and saved filehandles and current/saved stateids.
- Handle NFSv4 OPEN create/lookup semantics, including exclusive create verifier behavior.
- Validate writable/supported attributes, ACL/security-label support, and create/setattr attribute masks.
- Invoke lower NFSD VFS helpers for read, write, commit, create, remove, rename, link, readdir, readlink, xattr, fallocate, clone, copy, seek, and setattr.
- Manage server-side synchronous and asynchronous COPY, including inter-server copy support when enabled.
- Bridge pNFS protocol operations to layout drivers and layout state management.
- Compute maximum reply sizes for preflight response-space checks.
- Provide the NFSv4 procedure table and `nfsd_version4`.

Important entry points and exports:
- `nfsd4_proc_null()` handles NFSv4 NULL.
- `nfsd4_proc_compound()` is the central COMPOUND executor.
- `OPDESC()`, `nfsd4_cache_this_op()`, `nfsd4_max_reply()`, and `warn_on_nonidempotent_op()` are helper interfaces for operation metadata and encode safety.
- `nfsd4_spo_must_allow()` checks whether a compound includes a machine-credential-allowed operation.
- `nfsd4_has_active_async_copies()`, `nfsd4_async_copy_reaper()`, `nfsd4_shutdown_copy()`, and `nfsd4_cancel_copy_by_sb()` manage async COPY lifetime outside normal request execution.
- `nfsd_version4` exposes the NFSv4 service version with NULL and COMPOUND procedures.

Core COMPOUND flow:
- `nfsd4_proc_compound()` initializes response stream state, current/save filehandles, minor version, and disables request deferral.
- It rejects unsupported minor versions before other checks.
- `nfs41_check_op_ordering()` enforces NFSv4.1+ requirements for first operation/session context.
- For each decoded op, it honors decoder-preset status, validates filehandle presence, migrated exports, and response space for non-idempotent operations.
- It imports current stateid when configured, calls the operation handler, exports current stateid on success, clears stateid for operations flagged `OP_CLEAR_STATEID`, and performs wrongsec checks after putfh-like operations when required.
- It encodes either replay data or the operation result, increments per-op stats, clears replay state, and stops on first failing status.
- Current and saved filehandles are released at completion.

Open/create behavior:
- `nfsd4_open()` validates open/create combinations, reclaim rules, sessions, seqid/replay state, grace-period behavior, and open claims.
- `do_open_lookup()` performs regular path lookup or create, verifies the resulting object is regular, stores open-owner replay filehandle for v4.0, checks permissions, and sets change info.
- `nfsd4_create_file()` implements unchecked, guarded, exclusive, and exclusive4_1 create semantics with verifier stored via atime/mtime, ACL/security label handling, and post-create setattr.
- `do_open_fhandle()` handles claim-by-current-filehandle paths and delegation-current-filehandle behavior.
- `nfsd4_open_omfg()` handles decode-time seqid-mutating OPEN errors so v4.0 open-owner sequence state is still advanced correctly.

Major operation groups:
- Filehandle operations: `GETFH`, `PUTFH`, `PUTROOTFH`, `PUTPUBFH`, `SAVEFH`, `RESTOREFH`, and parent lookup.
- Metadata/data operations: `ACCESS`, `GETATTR`, `SETATTR`, `VERIFY`, `NVERIFY`, `READ`, `READ_PLUS`, `WRITE`, `COMMIT`, `READDIR`, `READLINK`, `CREATE`, `LINK`, `REMOVE`, `RENAME`, `SECINFO`, `SECINFO_NO_NAME`.
- State operations delegated to state code through the operation table: `CLOSE`, `LOCK`, `LOCKT`, `LOCKU`, `OPEN_CONFIRM`, `OPEN_DOWNGRADE`, `DELEGRETURN`, `RENEW`, client/session operations, `TEST_STATEID`, `FREE_STATEID`, and reclaim completion.
- NFSv4.2 operations: `ALLOCATE`, `DEALLOCATE`, `CLONE`, `COPY`, `COPY_NOTIFY`, `OFFLOAD_STATUS`, `OFFLOAD_CANCEL`, `SEEK`, and xattr operations.
- pNFS operations when enabled: `GETDEVICEINFO`, `LAYOUTGET`, `LAYOUTCOMMIT`, `LAYOUTRETURN`.

COPY/offload behavior:
- `nfsd4_verify_copy()` validates saved source and current destination stateids and ensures both files are regular.
- `nfsd4_setup_intra_ssc()` handles same-server copy setup.
- `nfsd4_setup_inter_ssc()` and related helpers handle inter-server source mounts when `CONFIG_NFSD_V4_2_INTER_SSC` is enabled.
- `nfsd4_copy()` dispatches synchronous or asynchronous copy. Async copies allocate a persistent copy object, create copy state, cap pending copies by server thread count, enqueue on the client async list, and start a kthread.
- `nfsd4_do_async_copy()` performs copy work, handles inter-server open/cleanup, records final status, updates cmtime for no-cmtime files, decrements pending async count, and sends `CB_OFFLOAD`.
- `nfsd4_offload_status()` reports active/completed async copy state.
- `nfsd4_offload_cancel()` cancels async copy or manages completed notification state.
- Reaper/shutdown/cancel-by-superblock paths prevent stale async copies from blocking client or filesystem teardown.

pNFS integration:
- `nfsd4_layout_verify()` checks export support and layout type bounds.
- `nfsd4_getdeviceinfo()` maps device IDs back to exports, calls layout driver `proc_getdeviceinfo`, and masks supported notification types.
- `nfsd4_layoutget()` validates iomode, permissions, ranges, layout stateid, recall conflicts, calls the layout driver, and records the granted layout.
- `nfsd4_layoutcommit()` validates size changes, grace/reclaim rules, layout stateid, calls driver commit, and marks delegation-written state.
- `nfsd4_layoutreturn()` validates iomode and return type, then delegates to layout-return helpers in `nfs4layouts.c`.

State and synchronization:
- Uses `struct nfsd4_compound_state` to track minor version, client/session, slot, current/save filehandles, current/save stateids, replay owner, and SPO machine-credential result.
- Async copy lists are protected by `clp->async_lock`; client hash/LRU scans use `nn->client_lock`.
- Pending async copy count is atomic per netns.
- Server-side inter-SSC mount list uses `nn->nfsd_ssc_lock` and wait queue coordination for busy mount entries.
- Filehandle pre/post attributes are cleared before each op and filled by VFS helpers for change-info replies.
- Non-idempotent ops are preflighted for response space to avoid performing mutations whose successful reply cannot be encoded.

Dependencies and integration:
- Calls extensive NFSD VFS helpers from `vfs.h`, state helpers from `state.h`, ACL helpers, idmap/XDR helpers, pNFS helpers, and tracepoints.
- Uses Linux VFS APIs for create, xattr, fallocate, llseek, fsync, mount, and file range copy.
- Uses kthreads for asynchronous copy and callback framework for `CB_OFFLOAD`.
- Uses SUNRPC request/transport constraints for payload sizing and response encoding.
- Uses NFSv4 stateid current-state hooks declared in operation descriptors.

Error handling and notable risks:
- COMPOUND execution stops on first failing op status but must still encode the failing operation correctly.
- Decoder-preset OPEN errors require special handling to preserve seqid semantics.
- Non-idempotent operations rely on reply-size estimates; underestimates risk warnings or protocol-visible failures after mutation.
- Async copy has multiple lifetime owners: client list, kthread, callback, reaper, cancel path, and filesystem teardown path.
- Inter-server copy is gated by module parameter and config; failures map to offload-denied/notsupp style protocol errors.
- pNFS layout operations must coordinate with layout recall state to avoid granting conflicting layouts.
- Several operations are grace-period sensitive and return `nfserr_grace` or `nfserr_no_grace` depending on reclaim state.
