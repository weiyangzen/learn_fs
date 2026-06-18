## sources/user-network-fs/libtirpc/src/getrpcport.c

Purpose: Implements the legacy `getrpcport` convenience wrapper that resolves a host and asks portmapper for a program/version/protocol port.

Important APIs and control flow: The function asserts a non-null host, resolves it with `gethostbyname`, initializes an IPv4 `sockaddr_in`, copies at most the address field size from `hostent`, and calls `pmap_getport`.

State and persistence: No persistent local state. It depends on resolver state and remote portmapper registration state.

Dependencies and integration: Uses IPv4-only legacy name resolution and the pmap compatibility layer. It is exported in the base map.

Risks and test signals: IPv6 is unsupported and `gethostbyname` returns static resolver storage. Tests should cover unknown host returning 0, long `h_length` truncation, successful pmap delegation, and protocol value pass-through.
