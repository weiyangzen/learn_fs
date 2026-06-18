# sources/user-network-fs/libtirpc/tirpc/rpc/clnt_soc.h

Purpose: `clnt_soc.h` exposes legacy socket-specific client constructors for backward compatibility with pre-TI-RPC APIs.

Important APIs, types, and functions: It defines `UDPMSGSIZE` and declares `clnttcp_create`, `clntraw_create`, optional IPv6 `clnttcp6_create`, `clntudp_create`, `clntudp_bufcreate`, and optional IPv6 UDP constructors.

Control flow: Callers pass `sockaddr_in`/`sockaddr_in6`, program/version, optional socket pointer, timeout for UDP, and buffer sizes. Implementations create the appropriate modern connection-oriented, datagram, or raw `CLIENT`.

State and persistence behavior: The header owns no state. Socket ownership is negotiated through the socket pointer and ultimately through client destroy/close controls.

Dependencies and integration points: It is included at the end of `clnt.h` for backward compatibility and maps old TS-RPC user code onto libtirpc client implementations.

Risks: IPv6 declarations are hidden behind `INET6`, so build flags affect ABI visibility. Legacy `u_long` program/version types must map correctly to 32-bit RPC types. `UDPMSGSIZE` is an RPC-imposed packet bound that may not match transport MTU.

Test signals: Compatibility tests should compile old `clnttcp_create`/`clntudp_create` callers, verify socket reuse/creation behavior, and cover optional IPv6 declarations where enabled.
