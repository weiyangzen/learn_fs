# sources/user-network-fs/libtirpc/tirpc/rpc/rpc_com.h

Purpose: `rpc_com.h` declares internal common helpers shared by client, server, rpcbind, and transport-selection code.

Important APIs, types, and functions: It defines `RPC_MAXDATASIZE`, `RPC_MAXADDRSIZE`, `__RPC_GETXID`, and prototypes for address size, fd table size, netconfig lookup, default domain, universal address conversion by address family, address fixup, sockinfo/netid conversion, semantics/socket-type conversion, null procedure calls, socket-bound checks, rpcbind address discovery, global `rpc_control`, and token parsing.

Control flow: Internal code uses these helpers to generate XIDs, convert between netconfig and sockets, locate rpcbind addresses, and implement global RPC controls.

State and persistence behavior: The header declares no state, but helpers operate on process fd limits, environment/configuration, netconfig data, and rpcbind/client handles.

Dependencies and integration points: It depends on RPC base types, `CLIENT`, `netconfig`, `netbuf`, and `__rpc_sockinfo` definitions from other headers. `svc_vc.c` uses several declarations from this header.

Risks: This is marked internal and not stable for applications. `__RPC_GETXID` mixes pid and timeval fields; uniqueness depends on call timing. Transport conversion helpers must preserve IPv4/IPv6 and netid semantics exactly.

Test signals: Tests should cover socket-info round trips, netid mappings, universal address conversions, bound-socket detection, XID uniqueness under rapid calls, and rpcbind find-address behavior.
