# sources/user-network-fs/samba/source3/lib/cluster_support.c

Purpose: reports whether Samba was built with CTDB cluster support and resolves CTDB feature/default socket information.

Important APIs/types/functions: `cluster_support_available()`, `cluster_support_features()`, and `lp_ctdbd_socket()`.

Control flow: compile-time `CLUSTER_SUPPORT`, `CTDB_SOCKET`, and `CTDB_PROTOCOL` conditionals determine feature strings and availability. `lp_ctdbd_socket()` prefers configured `lp__ctdbd_socket()` when non-empty, then compile-time `CTDB_SOCKET`, else empty string.

State and persistence: stateless; returns static string data or configuration-derived pointers.

Dependencies/integration: loadparm/private `lp__ctdbd_socket()`, CTDB protocol headers when clustering is compiled, and `tdb.h`.

Risks/test signals: missing cluster support must return false and feature text `NONE`; empty socket strings will cause CTDB open/probe failures elsewhere. Tests should cover clustered and non-clustered builds, configured socket override, compile-time socket fallback, and feature string content.
