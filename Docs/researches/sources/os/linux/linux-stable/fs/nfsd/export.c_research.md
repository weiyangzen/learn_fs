# File Research: sources/os/linux/linux-stable/fs/nfsd/export.c

## Summary
Implements NFSD export validation, export lookup, and export cache management. It owns two SunRPC caches: `nfsd.export`, mapping client/path to `svc_export` options, and `nfsd.fh`, mapping client/fsid fragments to export paths.

## Main APIs
- `nfsd_export_init()`, `nfsd_export_shutdown()`, `nfsd_export_flush()`.
- `nfsd_export_wq_init()` / `nfsd_export_wq_shutdown()` for deferred RCU release work.
- `rqst_exp_get_by_name()`, `rqst_exp_find()`, `rqst_exp_parent()`, `rqst_find_fsidzero_export()`.
- `exp_rootfh()` and `exp_pseudoroot()` compose root filehandles.
- `check_xprtsec_policy()`, `check_security_flavor()`, and `check_nfsd_access()` enforce transport and auth policy.

## Behavior
`svc_export_parse()` consumes mountd cache records with path, flags, anon uid/gid, fsid, optional UUID, NFSv4 fs locations, security flavor lists, and transport security modes. `check_export()` rejects unsupported object types, non-identifiable filesystems, missing export operations, idmapped mounts, and subtree-check requests on filesystems that opt out. Lookup first tries AUTH_SYS client exports, then falls back to GSS client exports where appropriate.

## State and Synchronization
Export and expkey objects are `cache_head` entries released via `queue_rcu_work()` on the `nfsd_export` workqueue. Per-export stats use percpu counters. Cache flushing purges the NFSD file cache under `nfsd_mutex`.

## Risks
Export lifetime is split across SunRPC cache refs, path refs, auth-domain refs, layout-device maps, and deferred RCU work. Security decisions combine xprtsec and flavor policy, so callers that bypass `check_nfsd_access()` can accidentally skip one half of the authorization model.
