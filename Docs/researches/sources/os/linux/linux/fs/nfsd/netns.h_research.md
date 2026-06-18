# File Research: sources/os/linux/linux/fs/nfsd/netns.h

Read completely: 247 lines.

Per-network-namespace NFSD state definition. `struct nfsd_net` is the central container for export caches, idmap caches, NFSv4 client/session/state tracking, duplicate reply cache state, service stats, filecache disposal, localio clients, and net lifetime management.

Key responsibilities:
- Defines client/session hash sizes and the per-net stats counter enum, including duplicate reply cache, filehandle stale, I/O byte counters, and NFSv4 operation counters.
- Declares `struct nfsd_net` with export and expkey cache pointers, id mapping caches, NFSv4 lock manager/grace/boot data, client tracking tables, session tables, laundromat work, lock lists, reclaim state, write verifier, service info, net refcount/completions, server-to-server copy state, supported protocol versions, duplicate reply cache metadata, counters, svc stats, shrinkers, copy mount tracking, server name, filecache disposal queue, siphash keys, courtesy client state, localio client list, filehandle key, and callback state.
- Provides `nfsd_netns_ready` and declares `nfsd_net_id`, version support, net reference helpers, and write verifier helpers.

Dependencies:
- Pulls in net namespace, filelock, NFSv4, percpu counter/refcount, siphash, and sunrpc stats infrastructure.

Notable risks:
- Many fields have different locking rules: client mutex, `deleg_lock`, `client_lock`, `blocked_locks_lock`, `s2s_cp_lock`, `nfsd_ssc_lock`, and localio lock.
- Shutdown order is complex because caches, nfsd service threads, duplicate reply cache, NFSv4 state, filecache disposal, and LOCALIO clients all have per-net lifetime.
