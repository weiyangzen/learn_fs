# sources/user-network-fs/samba/source3/lib/cluster_support.h

Purpose: exposes cluster support capability helpers.

Important APIs/types/functions: declarations for `cluster_support_available()`, `cluster_support_features()`, and `lp_ctdbd_socket()`.

Control flow: callers query availability before using CTDB-dependent features and call `lp_ctdbd_socket()` for the runtime socket path.

State and persistence: no public state.

Dependencies/integration: expected to be included by DB, messaging, and command-line helpers that need compile/runtime cluster decisions.

Risks/test signals: header lacks include guards in this snapshot, so repeated inclusion depends on compiler tolerance for repeated identical prototypes. Compile tests should include it from multiple translation units and verify no conflicting declarations.
