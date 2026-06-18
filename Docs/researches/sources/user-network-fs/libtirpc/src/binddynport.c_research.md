## sources/user-network-fs/libtirpc/src/binddynport.c

Purpose: Provides `__binddynport(int fd)`, a libtirpc internal helper that binds an unbound IPv4/IPv6 socket to a random dynamic/private port in the RFC 6335 range 49152-65534 while avoiding Linux locally reserved ports.

Important APIs and control flow: `is_reserved` and `set_reserved` maintain a compact bitset for the dynamic range. `parse_reserved_ports` reads `/proc/sys/net/ipv4/ip_local_reserved_ports`, accepts comma-separated singleton/range syntax, and marks excluded ports. `__binddynport` first returns success for already-bound sockets, then under `port_lock` calls `getsockname`, finds the port field by address family, seeds `rand_r`, builds the reserved-port bitset, and iterates through candidate ports until `bind` succeeds or a non-`EADDRINUSE` failure occurs.

State and persistence: Uses a static pseudo-random seed and reads live kernel configuration on each call. It does not persist bindings outside the socket state.

Dependencies and integration: Depends on `__rpc_sockisbound`, POSIX sockets, `/proc`, syslog, and the shared `port_lock` from `mt_misc.c`. It complements `bindresvport_sa` for non-privileged client sockets.

Risks and test signals: Linux `/proc` parsing failures prevent binding. The random seed is not cryptographic. Tests should cover empty/reserved-port files, range wraparound, already-bound sockets, IPv4/IPv6 family handling, and concurrent callers.
