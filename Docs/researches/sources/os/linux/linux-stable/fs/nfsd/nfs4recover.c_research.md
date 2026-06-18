# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4recover.c

Purpose: implements NFSv4 client recovery tracking for NFSD. It records clients on stable storage, reloads reclaimable clients after reboot, validates reclaim attempts during grace, and supports multiple tracking backends: `nfsdcld` rpc_pipefs, older nfsdcld protocol, usermode-helper `nfsdcltrack`, and optional legacy recovery directories.

Key structures and state:
- `struct nfsd4_client_tracking_ops` abstracts backend operations: init, exit, create, remove, check, grace_done, version, and message length.
- Legacy tracking stores MD5-hashed client-name directories under `/var/lib/nfs/v4recovery` by default.
- `struct cld_net` owns the rpc_pipefs pipe, outstanding upcall list, XID allocator, and legacy-detection flag.
- `struct cld_upcall` represents one synchronous nfsdcld upcall/downcall transaction.
- Reclaimable clients are loaded into `nn->reclaim_str_hashtbl`, shared with state recovery logic.

Major logic:
- Legacy directory mode overrides credentials to root, opens the recovery directory, creates/removes per-client directories, fsyncs stable storage, loads existing directory names into reclaim records, and purges non-reclaimed records after grace.
- Legacy client names are MD5 hex digests with fixed `HEXDIR_LEN`; v2 cld principal protection uses SHA-256 of the authenticated principal when available.
- rpc_pipefs mode creates an `nfsd/cld` pipe, queues upcalls, waits for completions, handles pipe reopen `-EAGAIN`, and processes downcalls by XID.
- `__cld_pipe_inprogress_downcall()` handles `Cld_GraceStart` streaming downcalls that populate reclaim records while the daemon is still processing startup.
- nfsdcld v0 checks each client directly; newer nfsdcld versions slurp clients at grace start and then check the in-kernel reclaim hash.
- v2 nfsdcld create/check includes principal hash data, preventing a client name alone from authorizing reclaim when a principal hash is recorded.
- Grace completion notifies the selected backend and releases in-kernel reclaim records when appropriate.
- UMH `nfsdcltrack` backend formats command arguments and environment variables for init/create/remove/check/gracedone, including legacy conversion paths and whether the client has sessions.
- `nfsd4_client_tracking_init()` chooses a backend: modern nfsdcld, older nfsdcld v0 fallback, then optional UMH/legacy methods if configured.
- Public wrappers `nfsd4_client_record_create/remove/check()` and `nfsd4_record_grace_done()` dispatch through the selected backend.
- rpc_pipefs mount/umount notifier registers or unlinks the cld pipe when rpc_pipefs instances appear or disappear.

Concurrency and lifetime:
- cld upcall lists and XID allocation are protected by `cn_lock`.
- Upcalls wait on completions; failed queued pipe messages complete waiters in `cld_pipe_destroy_msg()`.
- UMH client tracking serializes per-client create/remove/check with `NFSD4_CLIENT_UPCALL_LOCK`.
- Legacy directory iteration first builds an in-memory namelist to avoid mutating a directory while iterating it directly.
- Backend init/shutdown owns reclaim hash allocation and pipe or directory references per network namespace.

Important dependencies:
- Uses crypto MD5 and SHA-256 helpers for stable client identifiers and principal hashes.
- Uses rpc_pipefs APIs for nfsdcld communication and usermodehelper APIs for `nfsdcltrack`.
- Integrates with NFSD state recovery via `nfs4_client_to_reclaim()`, `nfsd4_find_reclaim_client()`, `nfs4_release_reclaim()`, and `nfs4_has_reclaimed_state()`.

Risk/edge cases:
- Legacy and UMH backends are rejected in non-init network namespaces.
- Missing or non-executable `nfsdcltrack` disables the UMH program path until an admin re-enables it.
- nfsdcld startup waits briefly for pipe readers/writers to avoid 30-second upcall timeouts during backend probing.
- Principal-hash mismatch in v2 tracking rejects reclaim even if the client name matches.
- If recovery tracking cannot initialize, NFSD warns that `nfsdcld` may not be running or legacy tracking may need enabling.
