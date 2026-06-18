# File Research: sources/os/plan9/plan9/sys/src/9/pc/devether.c

Generic PC Ethernet device multiplexer and card probing glue for Plan 9 `#l`.

Key responsibilities:
- Maintains discovered `Ether` controllers in `etherxx`.
- Implements devtab operations through the generic `netif` layer.
- Dispatches controller-specific attach, statistics, control, transmit, shutdown, and reset hooks.
- `etheriq()` demultiplexes received Ethernet packets to matching `Netfile`s by EtherType/promiscuous/multicast/address criteria.
- `etheroq()` handles outbound queueing, local loopback/promiscuous/broadcast feedback, and transmit kick.
- Supports packet header tracing for header-only listeners.
- Parses Ethernet addresses from hex strings.
- Registers card drivers through `addethercard()`.
- Probes configured `etherN` entries first, then auto-probes registered card types unless `*noetherprobe` is set.
- Sizes netif input/output queues based on interface Mbps, with memory caps.
- Provides a slow Ethernet CRC32 helper.

Important behavior:
- Outbound writes set the packet source address to the interface MAC.
- Multicast packets are dropped unless broadcast, promiscuous mode, or active multicast membership matches.
- Bridged packets are filtered from local feedback unless originated locally.
- IRQ2 is remapped to IRQ9.
- A negative `ether->irq` means no interrupt is used.

Dependencies:
- Depends on `etherif.h`, `../port/netif.h`, queue/block APIs, card-specific reset hooks, and Plan 9 devtab helpers.

Notable risks:
- Queue sizing is heuristic and tied to `mainmem->maxsize`.
- `etheriq` optimizes by passing the original received block to one recipient and copying for others; callers must respect ownership return semantics.
