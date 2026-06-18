# File Research: sources/os/plan9/plan9/sys/src/9/port/devbridge.c

Implements `#B`, an in-kernel IPv4 Ethernet bridge device with up to four bridge instances and 128 ports per bridge. The exposed namespace is `bridgeN/{ctl,stats,cache,log,<port>/ctl,<port>/local,<port>/status}`.

Key structures are `Bridge`, `Port`, and `Centry`. `Bridge` owns the port table, MAC-address cache, counters, delay settings, TCP MSS clamp flag, and log state. `Port` tracks bound ether/tunnel endpoints, reader process, owner hash, and packet statistics. `Centry` maps Ethernet addresses to bridge ports with expiry and hit counters.

Control operations on `ctl` include `bind ether|tunnel`, `unbind`, `cacheflush`, `set/clear tcpmss`, and `delay delay0 delayn`. Ether ports are opened through an underlying Ethernet clone/control/data path and placed into promiscuous bridge mode. Tunnel ports use separate read/write channels.

Packet flow is handled by a per-port `etherread` kernel process. It reads blocks, learns source MACs, optionally clamps TCP MSS in IPv4 TCP SYN packets, applies artificial delay, then either floods multicast/unknown traffic or forwards known unicast traffic using the cache. The cache avoids multicast/broadcast entries and expires entries after five minutes.

Tunnel output supports IPv4 fragmentation when packets exceed `TunnelMtu`, provided packets are IPv4 without IP options and not DF. `etherwrite` constructs Ethernet/IP fragments, updates IP length/fragment fields/checksums, and pads undersized Ethernet frames.

Dependencies include Plan 9 block I/O, `netif`, Ethernet/IP header definitions, `Log`, `kproc`, `namec`, and device-table dispatch. Main operational risks are all bridge state being protected by a single `QLock`, reader-process lifetime depending on notes during unbind, and low-level packet mutation/fragmentation requiring exact packet layout assumptions.
