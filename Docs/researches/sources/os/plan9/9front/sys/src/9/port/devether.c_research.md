# File Research: sources/os/plan9/9front/sys/src/9/port/devether.c

Purpose: generic Ethernet device front-end `#l`, multiplexing hardware NIC drivers into Plan 9 netif channels, plus netconsole and dynamic MAC address translation support.

Exposed interface: standard netif clone/control/data files supplied through `netif*` helpers. Attach specs select controller and may create eve-only configured instances with `ctlr:type/options`.

Core implementation: `addethercard` registers driver reset functions. `etherprobe` allocates/configures an `Ether`, parses config/options, calls the matching hardware reset, creates the output queue, initializes netif state, and records MAC/broadcast values. `etherreset` probes configured and auto-detected cards, installs `%E`, and enables netconsole if configured. `ethershutdown` calls hardware shutdown callbacks.

Packet paths: `etheriq` handles received blocks, optional DMAT downstream translation, stats, and `ethermux`. `etherwrite`/`etherbwrite` validate MTU, parse non-data controls such as `nonblocking`, defer driver ctl commands, and queue outbound packets via `etheroq`. `ethermux` delivers packets to matching netif connections, supports promiscuous, bridge, bypass, header-only trace, multicast, MAC learning, and copy avoidance.

Extra support: `netconsole` builds a UDP/IP/Ethernet console output path from `console=net ...`. `dmatproxy` rewrites MACs in ARP, IPv4/IPv6, NDP, and BOOTP cases to support bridging over media that cannot spoof source MACs.

Dependencies: `netif.h`, `etherif.h`, IP/IPv6 helpers, queue subsystem, hardware driver callbacks, and optional DMAT table in `Ether`.

Research notes: review should focus on packet ownership/freeing across `ethermux`, bridge/bypass interactions, q bypass changes on link state, DMAT checksum/address rewriting, and netconsole packet header construction.
