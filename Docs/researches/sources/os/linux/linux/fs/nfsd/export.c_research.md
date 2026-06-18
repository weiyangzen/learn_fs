# File Research: sources/os/linux/linux/fs/nfsd/export.c

Read completely: 1595 lines.

NFSD export cache implementation and validation logic. It maintains the two sunrpc caches that connect client identities to exported paths and fsid/filehandle fragments, parses mountd export updates, validates filesystem exportability, checks per-export security policy, exposes exports via seq_file, and manages per-net namespace export cache lifecycle.

Key responsibilities:
- Implements the expkey cache (`nfsd.fh`) mapping auth domain plus fsid type/value to an exported path, including upcall request formatting, userspace parse/update handling, hash/match/init/update callbacks, and deferred RCU work release.
- Implements the export cache (`nfsd.export`) mapping auth domain plus path to `struct svc_export` options, including path parsing, expiry, flags, anon uid/gid, fsid, UUID fsid, NFSv4 fs_locations, secinfo, xprtsec modes, pNFS layout setup, and export stats.
- Validates exports in `check_export`: only directories, symlinks, and regular files; V4ROOT is forced read-only; non-device filesystems need fsid or UUID; filesystems must have usable export operations; idmapped mounts are rejected; subtree checking is rejected when the filesystem forbids it.
- Provides lookup APIs used by request processing: `rqst_exp_get_by_name`, `rqst_exp_find`, `rqst_exp_parent`, `rqst_find_fsidzero_export`, `exp_rootfh`, and `exp_pseudoroot`.
- Enforces access policy via `check_xprtsec_policy`, `check_security_flavor`, and `check_nfsd_access`, combining TLS/mTLS transport requirements with RPC auth flavor/secinfo rules and selected GSS bypass behavior.
- Formats `/proc/fs/nfsd/exports` and export stats output, including option names, fsid, anon credentials, fs_locations, UUIDs, secinfo runs, and per-export stale/read/write counters.
- Initializes, flushes, and shuts down per-net export and expkey caches; module-level release work is drained with `rcu_barrier()` and `flush_workqueue()`.

Important interactions:
- Uses sunrpc cache infrastructure (`cache_detail`, `sunrpc_cache_lookup_rcu`, `sunrpc_cache_update`, `cache_check`, `cache_purge`).
- Uses auth domains, nfsd file cache purge on expkey flush, VFS path/exportfs helpers, pNFS layout setup, request security state, and `nfsd_net` per-net cache pointers.
- Deferred object freeing depends on the module-level `nfsd_export_wq`.

Notable risks:
- Export parsing accepts a stream of positional tokens from userspace; validation order is intentional, especially for dummy exportfs probes and anon uid/gid checks.
- Security behavior depends on subtle fallback between `rq_client` and deprecated GSS client domains, and on secinfo list presence.
- Shutdown correctness depends on draining RCU callbacks and queued release work before destroying per-net cache storage.
