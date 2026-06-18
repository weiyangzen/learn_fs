# File Research: sources/os/plan9/plan9/sys/src/9/kw/devether.c

## Purpose
Implements the generic Plan 9 Ethernet device `#l` for this port. It wraps controller-specific drivers behind a common `Ether`/`Netif` interface and handles channel operations, packet fanout, loopback, card registration, reset, shutdown, and CRC utilities.

## Main Behavior
- `etherattach`, `etherwalk`, `etherstat`, `etheropen`, `etherclose`, `etherread`, `etherbread`, `etherwrite`, and `etherbwrite` implement the device interface by delegating to `netif` helpers and controller callbacks.
- `etheriq` receives an Ethernet frame, validates multicast interest, determines local/broadcast/promiscuous delivery, fans packets out to matching `Netfile`s, and optionally avoids a copy for one receiver.
- `etheroq` handles outgoing packets, loops back local/broadcast/promiscuous-visible frames, queues non-loopback traffic to the controller output queue, and calls the controller transmit callback.
- `etherrtrace` emits compact trace records for header-only listeners.
- `addethercard` registers controller reset functions by type.
- `parseether` parses colon-separated MAC strings.
- `etherreset` asks `archether` for platform devices, matches registered card types, parses options, invokes controller reset, enables interrupts, initializes `netif`, allocates output queues, and publishes `etherxx`.
- `ethershutdown` calls controller shutdown hooks before reboot.
- `ethercrc` computes Ethernet CRC slowly in software.
- `dumpnetif` and `dumpoq` provide diagnostic printing.

## Dependencies and Integration
Uses platform discovery via `archether`, controller drivers registered by `addethercard`, Plan 9 `netif`, queues, blocks, interrupts, and Ethernet packet definitions.

## Risks and Notes
Packet fanout copies frames for all but one matching receiver. Controller-specific stats may be refreshed on reads of `ifstats` or `stats`. Output writes force the source MAC to the interface address for user-provided frames.
