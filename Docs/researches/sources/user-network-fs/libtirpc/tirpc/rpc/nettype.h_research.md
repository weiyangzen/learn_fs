# sources/user-network-fs/libtirpc/tirpc/rpc/nettype.h

Purpose: `nettype.h` defines internal nettype selector constants and helper prototypes for mapping high-level RPC nettype strings to `netconfig` entries.

Important APIs, types, and functions: It defines `_RPC_NONE`, `_RPC_NETPATH`, `_RPC_VISIBLE`, `_RPC_CIRCUIT_V`, `_RPC_DATAGRAM_V`, `_RPC_CIRCUIT_N`, `_RPC_DATAGRAM_N`, `_RPC_TCP`, and `_RPC_UDP`, plus `__rpc_setconf`, `__rpc_endconf`, `__rpc_getconf`, and `__rpc_getconfip`.

Control flow: Implementations use `__rpc_setconf` to start an internal netconfig iteration for a nettype, `__rpc_getconf`/`__rpc_getconfip` to fetch matching entries, and `__rpc_endconf` to release iteration state.

State and persistence behavior: Iterator state is opaque and implementation-owned. The header owns no state.

Dependencies and integration points: It depends on `netconfig.h` and is used by generic client/server creation, broadcast, and rpcbind address discovery.

Risks: Constants are private but widely used inside libtirpc; mismatches with parser logic can select wrong transports. Opaque handles require strict cleanup to avoid leaks.

Test signals: Tests should cover each named nettype string, TCP/UDP shortcuts, visible-only selection, `NETPATH` ordering, IPv4/IPv6 filtering, and cleanup after partial iteration.
