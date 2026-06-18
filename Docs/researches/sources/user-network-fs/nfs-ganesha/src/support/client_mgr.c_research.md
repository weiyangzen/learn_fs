<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/client_mgr.c -->
# sources/user-network-fs/nfs-ganesha/src/support/client_mgr.c

## Purpose
`client_mgr.c` manages live NFS-Ganesha client records keyed by network address and provides reusable export/client-list parsing and matching logic. When DBus is enabled, it also publishes client management and per-client statistics methods.

## Important APIs, Types, and Functions
The live-client store is `static struct client_by_ip`, containing an AVL tree, rwlock, and hash-front cache. Core APIs are `get_gsh_client`, `put_gsh_client`, `remove_gsh_client`, `foreach_gsh_client`, `client_pkginit`, and `client_mgr_cleanup`. DBus-facing helpers include `arg_ipaddr`, `lookup_client`, `dbus_client_init`, `reset_client_stats`, and `reset_clnt_allops_stats`. Export/client-list APIs include `StrClient`, `LogClientListEntry`, `LogClientList`, `FreeClientList`, `base_client_allocator`, `is_base_client_exact_match`, `add_client`, `delete_base_client`, `client_match`, and `haproxy_match`.

## Control Flow
`get_gsh_client` hashes the sockaddr, checks the front cache under a read lock, falls back to AVL lookup, and creates a new `server_stats`-backed `gsh_client` under a write lock if needed. It initializes locks and connection-manager state for new clients and returns with the client refcount incremented. `remove_gsh_client` removes an unused client from cache/tree, frees statistics and QoS memory, finalizes connection state, and destroys locks. `add_client` converts config tokens into base client entries: wildcard-any, netgroups, CIDR/address entries, wildcard host patterns, or resolved DNS names that may expand into multiple network entries. `client_match` checks client lists using CIDR containment, netgroup membership via IP-name cache, wildcard matching against IP and hostname, or match-any.

## State and Persistence Behavior
State is in-memory only: AVL nodes, cache slots, refcounts, per-client locks, statistics, connection-manager state, and configured base-client lists owned by callers. DBus methods expose and reset runtime statistics but do not persist them to disk.

## Dependencies and Integration Points
This file depends on pthread rwlocks, AVL and glist utilities, sockaddr/CIDR helpers, server statistics, FSAL/export management, QoS, IP-name and netgroup caches, DBus support, SAL connection functions, and global `nfs_param`. It integrates with request dispatch for client lookup, export access checks, HAProxy proxy-host validation, and management tooling under `/org/ganesha/nfsd/ClientMgr`.

## Risks and Test Signals
Risks include refcount lifetime mistakes, stale front-cache entries if removal paths miss a slot, DNS expansion producing duplicate or surprising entries, hostname/netgroup cache freshness, compile-time DBus/stat feature permutations, and the DBus `disconnect_nfsv41_client` path parsing the address twice while holding a client reference that is not explicitly released after disconnect. `client_match` is caller-locking dependent for configured lists. Test signals include concurrent get/remove stress, refcount assertions, DBus Add/Remove/Show/Get stats calls, duplicate client config errors, CIDR/netgroup/wildcard matching tests, IPv4-mapped IPv6 matching, HAProxy host list tests, and cleanup under sanitizers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/client_mgr.c -->
