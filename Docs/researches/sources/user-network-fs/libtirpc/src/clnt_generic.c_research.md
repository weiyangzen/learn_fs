## sources/user-network-fs/libtirpc/src/clnt_generic.c

Purpose: Implements high-level RPC client creation APIs that hide netconfig selection, rpcbind lookup, version negotiation, socket creation, and transport-specific client construction.

Important APIs and control flow: `clnt_create` and `clnt_create_timed` iterate netconfig entries for a nettype via `__rpc_setconf`, trying `clnt_tp_create_timed` until one succeeds while preserving more useful errors than final name-translation failures. `clnt_create_vers_timed` probes `NULLPROC`, adjusts version ranges from `RPC_PROGVERSMISMATCH`, and returns the highest supported version. `clnt_tp_create_timed` resolves service address with `__rpcb_findaddr_timed`, reuses a returned client when possible, or calls `clnt_tli_create`. `clnt_tli_create` opens/binds fds, raises low descriptors, verifies address family, then chooses `clnt_vc_create` or `clnt_dg_create` from netconfig semantics.

State and persistence: Uses global `rpc_createerr`/thread-specific create errors and `__rpc_minfd`. Created clients own sockets when opened internally.

Dependencies and integration: Connects netconfig, rpcbind, reserved-port binding, TCP_NODELAY, fd raising, and the dg/vc transports.

Risks and test signals: `__rpc_raise_fd` unexpectedly calls `fsync` on duplicated fds. Tests should cover version fallback, error preservation, fd ownership flags, address-family mismatches, nettype length rejection, and all netconfig semantics.
