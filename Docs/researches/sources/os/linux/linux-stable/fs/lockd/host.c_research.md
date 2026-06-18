# File Research: sources/os/linux/linux-stable/fs/lockd/host.c

Manages shared NLM peer host handles for client and server personalities.

Host cache:
- Uses separate hash tables for client and server hosts.
- Hashes IPv4/IPv6 peer addresses into 32 buckets.
- `nlm_alloc_host()` initializes address, RPC metadata, NSM handle, locks, reclaim/granted lists, refcount, expiry, credentials, and nodename.
- `nlmclnt_lookup_host()` matches client hosts by netns, address, protocol, and NLM version.
- `nlmsvc_lookup_host()` matches server hosts by netns, client address, source address, protocol, and version; it also triggers periodic GC.

RPC binding:
- `nlm_bind_host()` creates an RPC client with NLM program/version, UNIX auth, autobind, reuseport, optional hard retry for client-side calls, optional non-privileged source port, and optional source address.
- `nlm_rebind_host()` forces UDP portmap rebinds on a timed interval.
- `nlmclnt_shutdown_rpc_clnt()` marks a client shut down and cancels outstanding tasks.

Reboot and GC:
- `nlm_host_rebooted()` maps NSM reboot notifications to all affected hosts, frees server resources, and starts client recovery.
- `nlm_shutdown_hosts_net()` expires all matching server hosts, shuts down RPC clients, frees server resources, and runs GC.
- `nlm_gc_hosts()` marks hosts with active resources, then destroys expired unreferenced server hosts.
- Per-net and global host counters are maintained.

Synchronization:
- Global host cache is protected by `nlm_host_mutex`.
- Individual RPC client binding is protected by `host->h_mutex`.
