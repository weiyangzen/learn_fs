# File Research: sources/os/plan9/plan9/sys/src/9/port/netif.h

Defines the generic network interface structures and constants shared by Plan 9 network drivers and `netif.c`.

Main definitions:
- Qid type constants: `Ncloneqid`, `Naddrqid`, `N2ndqid`, `N3rdqid`, `Ndataqid`, `Nctlqid`, `Nstatqid`, `Ntypeqid`, `Nifstatqid`, `Nmtuqid`.
- Qid packing macros: `NETTYPE`, `NETID`, `NETQID`.
- `Netfile`: one multiplexed open/conversation, including owner/mode, type, promiscuous/scan/bridge/headersonly flags, multicast bitmask, and input `Queue`.
- `Netaddr`: multicast address node with allocation-chain link, hash-chain link, fixed-size address storage, and reference count.
- `Netif`: shared interface state: name, `Netfile` table, address/MTU/link data, multicast tables, counters, and hardware callback hooks.
- Ethernet constants and `Etherpkt` layout.

Exported operations:
- `netifinit`, `netifwalk`, `netifopen`, `netifclose`, `netifread`, `netifbread`, `netifwrite`, `netifwstat`, `netifstat`, `activemulti`.

Role in repository:
- This is the portable contract for network device implementations to expose Plan 9 network conversations through a uniform file interface.
