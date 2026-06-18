# File Research: sources/os/bsd/openbsd-src/sys/sys/domain.h

This header defines the protocol domain descriptor for kernel networking.

Key definitions:
- `socklen_t` typedef guard.
- Forward declaration for `struct mbuf`.
- `struct domain` with address family, name, init hook, rights externalize/dispose hooks, protocol switch range, sockaddr size, route key offset, and maximum prefix length.

Kernel APIs:
- `domaininit`
- Domain globals: `domains[]`, `inet6domain`, `inetdomain`, `mplsdomain`, `pfkeydomain`, `routedomain`, `unixdomain`.

Risk notes:
- `dom_externalize` and `dom_dispose` handle file-descriptor/access-right transfer over mbufs, so domain implementations must preserve ownership rules.
- Routing fields are used by generic route-table code and must match each domain’s sockaddr layout.
