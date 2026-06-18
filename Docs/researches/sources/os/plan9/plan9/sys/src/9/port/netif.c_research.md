# File Research: sources/os/plan9/plan9/sys/src/9/port/netif.c

Implements the reusable Plan 9 network-interface file-server layer used by network drivers. It exposes a three-level 9P-style namespace: top network directory, second-level `clone`/`addr`/`stats`/`ifstats` plus per-conversation directories, and third-level per-conversation `data`, `ctl`, `stats`, `type`, and `ifstats`.

Key responsibilities:
- `netifinit` initializes `Netif` name, conversation slots, and input queue limit.
- `netifwalk`, `netifopen`, `netifclose`, `netifread`, `netifbread`, `netifwrite`, `netifstat`, and `netifwstat` provide generic device operations for network drivers.
- `openfile` allocates or reopens `Netfile` conversations and input queues.
- `netown` lazily assigns ownership and enforces owner/eve/other permissions.
- `netifwrite` parses control commands: `connect`, `promiscuous`, `scanbs`, `bridge`, `headersonly`, `addmulti`, and `remmulti`.
- Multicast state is reference-counted globally in `Netaddr` lists/hash buckets and per-open in `Netfile.maddr`.
- `activemulti` checks whether a multicast address is actively referenced.
- Provides network byte-order helpers `hnputv`, `hnputl`, `hnputs`, `nhgetv`, `nhgetl`, `nhgets`.

Important behavior:
- Opening `clone` returns a control qid for a newly allocated conversation.
- Opening `data` or `ctl` increments `Netfile.inuse` and reopens its queue.
- Closing the last reference tears down promiscuous mode, scanning, multicast subscriptions, wildcard type count, owner, bridge/headersonly flags, type, and queue state.
- `typeinuse` prevents duplicate positive multiplexor types; negative types increment `nif->all`.
- `netifread` reports device counters and hardware address in text form.
- Driver-specific hardware hooks are invoked through `Netif.promiscuous`, `Netif.multicast`, and `Netif.scanbs`.

Dependencies:
- Queue operations from `qio.c`.
- Permission, channel, directory, and qid helpers from the Plan 9 port device layer.
- `netif.h` for `Netif`, `Netfile`, qid macros, and Ethernet constants.

Cautions:
- `netmulti` only tracks up to `8*sizeof(f->maddr)` multicast membership bits per `Netfile`; global references still exist beyond that index.
- `parseaddr` expects hex octets with optional colon separators and does not validate trailing garbage.
