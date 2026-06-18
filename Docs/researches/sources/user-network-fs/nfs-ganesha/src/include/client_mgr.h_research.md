<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/client_mgr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/client_mgr.h

## Purpose
`client_mgr.h` declares Ganesha client-host management APIs and data structures. It tracks connected clients by address, reference counts, per-state statistics, connection-manager state, and export access-list client entries.

## Important APIs, types, and functions
- `struct gsh_client` embeds an AVL node, client rwlock, atomic refcount, last update timestamp, printable host address, socket address, optional QoS class, per-state counters, and `connection_manager__client_t`.
- Inline helpers `inc_gsh_client_refcount()`, `inc_gsh_client_state_stats()`, and `dec_gsh_client_state_stats()` use atomic operations on refcounts and state counters.
- Package and DBus initialization APIs are `client_pkginit()` and optional `dbus_client_init()`.
- Client lookup/lifetime APIs are `get_gsh_client()`, `put_gsh_client()`, and `foreach_gsh_client()`.
- `enum exportlist_client_type` classifies access-list entries: protocol, network, netgroup, wildcard host, GSS principal, match-any, and bad client.
- `struct base_client_entry` stores an access-list item with list linkage, type, CIDR pointer, and string.
- Formatting/logging helpers include `get_base_client_str()`, `StrClient()`, `LogClientListEntry()`, `LogClientList()`, and convenience macros.
- Access-list mutation and matching APIs include `FreeClientList()`, `client_match()`, `add_client()`, `delete_base_client()`, and `haproxy_match()`.

## Control flow
The client package is initialized at server startup. Connection paths call `get_gsh_client()` with a socket address to find or create a client object, increment references while in use, and call `put_gsh_client()` when done. State owners increment/decrement per-state stats as NFS state objects are associated with clients. Export parsing builds lists of `base_client_entry` values; access checks call `client_match()` against a host string/address and optional predicate.

## State and persistence
Client objects are in-memory runtime state keyed by address in an AVL tree managed by implementation code. Refcounts control lifetime. State counters are atomic per client and reflect live server state. Export client lists are configuration-derived in memory and can be rebuilt on export reload.

## Dependencies and integration points
The header depends on pthreads, `avltree`, `gsh_types`, IP/CIDR utilities, SAL state types, connection manager types, optional QoS, DBus, config parser term types, and logging/display buffers. It integrates transport connection handling, export access control, HAProxy proxy matching, per-client state accounting, and management diagnostics.

## Risks
- Client lifetime depends on balanced `get_gsh_client()`/`put_gsh_client()` and atomic refcount correctness.
- AVL-key comparator and address normalization in implementation must handle IPv4/IPv6 and mapped addresses consistently.
- Export-list matching involves multiple client types and optional predicates; order and specificity can affect access decisions.
- State stats are counters only; underflow from unmatched decrement would corrupt diagnostics.
- `base_client_entry` ownership of `cidr` and `str` must be respected by list free/delete functions.

## Test signals
- Client manager tests should cover lookup-only misses, create hits, refcount put/free, foreach traversal, and concurrent lookups.
- Access-list tests should cover protocol, CIDR network, netgroup, wildcard host, GSS principal, match-any, delete, and predicate filtering.
- IPv4/IPv6 tests should verify address string formatting and matching normalization.
- State-counter tests should verify increments/decrements for each state type and guard against underflow.
- HAProxy integration tests should confirm proxied client matching behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/client_mgr.h -->
