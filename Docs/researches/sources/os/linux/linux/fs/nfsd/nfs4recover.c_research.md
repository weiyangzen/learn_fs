# File Research: sources/os/linux/linux/fs/nfsd/nfs4recover.c

This file implements NFSD NFSv4 client recovery tracking. It abstracts multiple stable-storage tracking backends, loads reclaimable clients at server startup, records/removes stable client records, verifies reclaim eligibility during the grace period, and registers rpc_pipefs notifications for `nfsdcld` communication.

Primary responsibilities:
- Define the `nfsd4_client_tracking_ops` backend interface.
- Support modern `nfsdcld` rpc_pipefs client tracking, including v1 and v2 message formats.
- Support older `nfsdcld` v0 behavior.
- Optionally support legacy recovery directory tracking and usermode-helper `nfsdcltrack` when configured.
- Maintain per-netns reclaim hash tables used during grace/reclaim.
- Create, remove, and check stable client records.
- End grace periods and purge/release reclaim records.
- Register/unregister rpc_pipefs notifier hooks so the `cld` pipe appears as rpc_pipefs mounts come and go.

Backend abstraction:
- `struct nfsd4_client_tracking_ops` has `init`, `exit`, `create`, `remove`, `check`, `grace_done`, `version`, and `msglen`.
- `nfsd4_client_tracking_init()` selects a backend: modern `nfsdcld`, old `nfsdcld`, then legacy methods if enabled.
- Public wrappers dispatch through the selected backend:
  - `nfsd4_client_record_create()`
  - `nfsd4_client_record_remove()`
  - `nfsd4_client_record_check()`
  - `nfsd4_record_grace_done()`
  - `nfsd4_client_tracking_exit()`

Modern `nfsdcld` rpc_pipefs path:
- `struct cld_net` stores the rpc pipe, lock, outstanding upcall list, xid counter, and optional legacy-detected flag.
- `struct cld_upcall` tracks one in-flight upcall and completion.
- `__nfsd4_init_cld_pipe()` allocates pipe data, initializes state, and registers the pipe under `nfsd/cld` in rpc_pipefs.
- `alloc_cld_upcall()` assigns a unique xid and links the upcall under `cn_lock`.
- `cld_pipe_upcall()` queues the message and waits for userspace completion, retrying `-EAGAIN`.
- `cld_pipe_downcall()` matches userspace replies by xid, supports `-EINPROGRESS` grace-start streaming records, copies final replies, and completes waiters.
- `nfsd4_cld_get_version()` negotiates userspace protocol version and switches to v2 ops when available.
- `nfsd4_cld_grace_start()` asks userspace to stream reclaim records into NFSD.
- `nfsd4_cld_create()`, `nfsd4_cld_create_v2()`, and `nfsd4_cld_remove()` update stable records.
- `nfsd4_cld_check()`, `nfsd4_cld_check_v2()`, and `nfsd4_cld_check_v0()` verify reclaim eligibility.
- `nfsd4_cld_grace_done()` notifies userspace and releases in-kernel reclaim records.

v2 principal handling:
- v2 create messages include a SHA-256 hash of the raw principal or principal string when present.
- v2 check verifies the reclaim record’s principal hash against the reconnecting client’s principal before allowing reclaim.
- This tightens recovery identity matching beyond the client-provided opaque client name.

Legacy recovery directory path when enabled:
- Uses `/var/lib/nfs/v4recovery` by default, configurable through `nfs4_reset_recoverydir()`.
- Client records are directories named by MD5 hash of the NFSv4 client owner string.
- `nfsd4_create_clid_dir()` creates a hashed directory and fsyncs the recovery directory.
- `nfsd4_remove_clid_dir()` removes the directory and updates in-grace reclaim records.
- `nfsd4_recdir_load()` scans existing directory names into reclaim records at startup.
- `nfsd4_recdir_purge_old()` removes entries not reclaimed by the end of grace.
- Legacy filesystem operations override credentials to global root while accessing the recovery directory.
- Legacy tracking is rejected for non-init network namespaces.

Usermode-helper `nfsdcltrack` path when enabled:
- Uses module parameter `cltrack_prog`, default `/sbin/nfsdcltrack`.
- Supports `init`, `create`, `remove`, `check`, and `gracedone` commands.
- Passes environment values for legacy topdir/recovery dir, whether the client has a session, and grace start time.
- Serializes per-client upcalls with `NFSD4_CLIENT_UPCALL_LOCK`.
- Disables the helper path by blanking `cltrack_prog` on `-ENOENT` or `-EACCES`.

State and synchronization:
- Reclaim hash tables live in `struct nfsd_net` and are allocated by `nfs4_cld_state_init()` or legacy state init.
- `track_reclaim_completes` and `nr_reclaim_complete` are initialized for cld tracking.
- `cn_lock` protects in-flight cld upcalls and xid allocation.
- Completions wake blocked kernel upcall senders after userspace downcalls.
- Legacy directory operations use mount write counts and fsync to make stable record updates durable.
- rpc_pipefs notifier callbacks take a module reference while registering/unlinking pipes on mount/umount events.

Dependencies and integration:
- Uses crypto MD5 for legacy directory names and SHA-256 for v2 principal hashes.
- Uses rpc_pipefs and SUNRPC pipe APIs for `nfsdcld`.
- Uses NFSD reclaim helpers such as `nfs4_client_to_reclaim`, `nfsd4_find_reclaim_client`, `nfs4_remove_reclaim_record`, `nfs4_release_reclaim`, and `nfs4_has_reclaimed_state`.
- Uses Linux VFS APIs for directory scanning, mkdir/rmdir, fsync, path lookup, and credential override.
- Called by NFSv4 state management during client create, reclaim, client expiry, grace completion, and server startup/shutdown.

Error handling and notable risks:
- `nfsd4_client_tracking_init()` warns and disables tracking if all backends fail; without tracking, reclaim support is unavailable.
- Modern cld init waits briefly for userspace to open the pipe to avoid 30-second pipe upcall timeouts.
- Downcall matching depends on xid uniqueness and userspace returning exact message sizes.
- `-EINPROGRESS` downcalls stream reclaim records during grace start and do not complete the original upcall.
- v2 principal mismatch denies reclaim even if the client name matches.
- Legacy recovery directory names are MD5 hashes for compatibility, not collision-resistant identity proofs.
- Usermode helper execution is unavailable in non-init netns and can be permanently disabled until reset if the helper is missing or not executable.
