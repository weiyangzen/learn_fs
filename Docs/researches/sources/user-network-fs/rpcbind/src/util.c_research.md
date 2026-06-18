<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/util.c -->
# sources/user-network-fs/rpcbind/src/util.c

Purpose: Provides network address utilities for rpcbind, primarily selecting the best server universal address for a caller on multi-homed systems and caching local RPC service addresses for remote-call forwarding.

Important APIs, types, and functions: Public functions are `addrmerge`, `network_init`, and `local_sa`. Internal helpers/macros include `bitmaskcmp`, `SA2SIN`, `SA2SINADDR`, and IPv6 variants. Static state stores `local_in4` and optional `local_in6`.

Control flow: `addrmerge` converts the caller and optional client hint universal address to transport addresses, treats local callers as direct-return cases, enumerates interfaces with `getifaddrs`, finds an exact or same-network interface matching the hint/caller family, copies that interface address, replaces its port with the registered service port, and converts it back to a universal address. `network_init` resolves local `sunrpc` IPv4/IPv6 addresses and, for IPv6 builds, joins the RPC multicast group on multicast-capable interfaces. `local_sa` returns the cached local address for a family.

State and persistence: Local address pointers are allocated during `network_init` and retained for daemon lifetime. No disk persistence. The selected addresses affect `rpcbproc_callit_com` forwarding behavior and `mergeaddr` semantics indirectly.

Dependencies and integration points: Depends on libtirpc address conversion (`taddr2uaddr`, `uaddr2taddr`, `rpcbind_get_conf`), POSIX `getifaddrs`, IPv4/IPv6 socket structures, `getaddrinfo`, and multicast socket operations. It is used by GETADDR/GETADDRLIST-style resolution and remote-call forwarding paths.

Risks: Interface selection relies on netmask comparisons and first/up interface heuristics; unusual routing, point-to-point interfaces, containers, or missing netmasks may produce surprising addresses. `network_init` does not free `local_in4/local_in6` during normal daemon lifetime. `addrmerge` has family-specific size handling and assumes service universal address conversion succeeds before port copy.

Test signals: Test callers from loopback, same subnet, different subnet, IPv6 link-local with scope id, explicit hint address, and local/unix addresses. Exercise hosts with multiple interfaces and point-to-point/loopback preferences. For IPv6, validate multicast join attempts are non-fatal and local_sa returns usable data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/src/util.c -->
