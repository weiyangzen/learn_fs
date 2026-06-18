# File Research: sources/os/bsd/netbsd-src/sys/sys/domain.h

Defines the network protocol domain structure and domain registration machinery.

Key content:
- Includes mbuf, socket, and route headers.
- `struct domain` fields for address family/name, init, rights externalize/dispose, protocol switch range, route table attach, route key metadata, interface up/down/attach/detach/link-state hooks, sockaddr address access/comparison/externalization, wildcard sockaddr, domain ifqueues, list linkage, mbuf owner, and sockaddr comparison offsets.
- Domain list heads.
- Kernel macros/functions: `DOMAIN_DEFINE`, `DOMAIN_FOREACH`, `domains`, `domain_attach`, `domaininit`, `domaininit_post`.

Important behavior:
- Provides the core registration contract for protocol families such as inet, inet6, unix, etc.
- Uses link sets for static domain registration.
