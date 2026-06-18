# File Research: sources/os/plan9/9front/sys/src/9/port/devbridge.c

Purpose: kernel Ethernet bridge device `#B`, supporting multiple bridge instances, VLAN-aware forwarding, MAC learning, tunnel/bypass ports, logging, stats, and optional TCP MSS clamping.

Exposed interface: `#B<n>/bridge<n>/` with bridge files `ctl`, `stats`, `cache`, `log`, and per-port directories containing `ctl`, `local`, and `status`. `ctl` supports `bind`, `unbind`, `vlan`, `cacheflush`, `set tcpmss`, `clear tcpmss`, and `delay`.

Core implementation: `Bridge` tracks ports, MAC cache, stats, delay parameters, MSS option, and log state. `Port` wraps one or two data Chans, owns a reader proc, identity tuple, owner hash, stats, and VLAN membership bitmap. `etherread` is the receive loop: reads packets, applies delay, strips/validates VLAN tags, learns source MACs, and forwards unicast or floods multicast/unknown traffic. `etherwrite` handles outgoing VLAN tagging, minimum frame sizing, and IPv4 fragmentation for tunnel ports.

Port setup: `portbind` opens Ethernet clone/data channels, configures promiscuous or bypass mode and bridge mode, or opens read/write tunnel endpoints. It inserts the port under bridge write lock and starts a reader kproc. `portunbind` posts a note to the reader and removes the port.

Dependencies: Plan 9 netif/Ethernet, IP/IPv6 helpers, logging helpers, and `tcpmssclamp`.

Research notes: key review areas are bridge lock upgrades in `etherread`, cache mutation under read/write locks, reader shutdown semantics, owner-hash race prevention, VLAN validation, and tunnel fragmentation correctness.
