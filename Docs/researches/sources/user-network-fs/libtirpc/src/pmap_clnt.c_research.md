## sources/user-network-fs/libtirpc/src/pmap_clnt.c

Purpose: Implements legacy portmapper registration wrappers over rpcbind APIs.

Important APIs and control flow: `pmap_set` accepts only UDP or TCP, obtains the corresponding inet netconfig via `__rpc_getconfip`, formats a universal address `0.0.0.0.high.low` from the requested port, converts it to a transport address with `uaddr2taddr`, and calls `rpcb_set`. `pmap_unset` attempts `rpcb_unset` for both UDP and TCP inet netconfigs and returns true if either succeeds for backward compatibility.

State and persistence: No local persistent state; it mutates remote/local rpcbind registration state.

Dependencies and integration: Bridges PMAP v2 compatibility APIs to rpcbind registration. Depends on netconfig conversion helpers.

Risks and test signals: Only IPv4 inet UDP/TCP are handled. Tests should cover invalid protocol rejection, netconfig lookup failure, universal-address conversion failure, cleanup of netconfig/netbuf, and partial unset success.
