# File Research: sources/os/linux/linux-stable/fs/nfsd/nfssvc.c

## Summary
Central NFSD service manager and dispatcher. It owns SunRPC program registration tables, protocol version enablement, service creation/destruction, per-net startup/shutdown, dynamic thread management, write verifier generation, and duplicate-reply-cache dispatch integration.

## Main APIs
- Version/service controls: `nfsd_support_version()`, `nfsd_vers()`, `nfsd_minorversion()`, `nfsd_reset_versions()`, `nfsd_create_serv()`, `nfsd_destroy_serv()`, `nfsd_svc()`.
- Thread controls: `nfsd_nrthreads()`, `nfsd_nrpools()`, `nfsd_get_nrthreads()`, `nfsd_set_nrthreads()`, `nfsd_shutdown_threads()`.
- Net refs and verifier: `nfsd_net_try_get()`, `nfsd_net_put()`, `nfsd_copy_write_verifier()`, `nfsd_reset_write_verifier()`.
- Runtime dispatch: `nfsd_dispatch()`, `nfssvc_decode_voidarg()`, `nfssvc_encode_voidres()`.

## Behavior
Startup creates a pooled SunRPC service, binds it, registers address notifiers, initializes lockd when NFSv2/v3 are enabled, starts file cache, reply cache, and NFSv4 state. The `nfsd` kernel thread loop receives RPC work, grows or shrinks worker counts opportunistically, and disposes per-net file-cache objects. Dispatch decodes arguments, marks request status fields stable for netlink observation, consults the duplicate reply cache, executes the procedure, encodes the reply, and updates the cache.

## State and Synchronization
`nfsd_mutex` protects `nn->nfsd_serv`, listener state, version configuration, and startup globals. Per-net lifetime during shutdown uses `percpu_ref` completion handshakes. Write verifier updates use a seqlock and SipHash. Address notifiers use `nfsd_notifier_lock` and a refcount shared across namespaces.

## Risks
Service teardown order matters: exports, state, reply cache, file cache, lockd, and generic resources have dependent lifetimes. Dynamic thread management relies on `svc_pool` limits and careful mutex trylock behavior. Dispatch’s `rq_status_counter` stability protocol must stay paired with parser/execution boundaries or netlink status dumps can observe inconsistent request data.
