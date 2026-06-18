# File Research: sources/os/bsd/dragonflybsd/sys/sys/domain.h

Network protocol domain registration structure header.

Key responsibilities:
- Defines `SLIST_HEAD(domainlist, domain)`.
- Defines `struct domain` with address family, name, init hook, externalize/dispose hooks, protocol switch range, list linkage, routing table attach data, interface attach/detach/up/down hooks, and AF-dependent ifnet data support.
- Declares kernel global domain list and local domain.
- Declares `net_add_domain`.
- Defines `DOMAIN_SET` SYSINIT registration macro.

Dependencies:
- Includes `sys/queue.h`; forward-declares mbuf and ifnet.
- Uses `struct protosw` defined elsewhere.

Notable risks:
- Domain registration order uses SYSINIT priority and affects protocol availability.
- Routing/interface hooks are per-address-family and must handle lifecycle symmetry.
