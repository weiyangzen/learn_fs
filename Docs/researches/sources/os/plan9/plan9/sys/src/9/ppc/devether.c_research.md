# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devether.c

## Role

Architecture-local Plan 9 Ethernet device frontend for `#l`, built on the generic `netif` layer and pluggable hardware reset routines.

## Main Data

`etherxx[MaxEther]` stores active controllers. `cards` registers hardware types through `addethercard`. Each controller is an `Ether` from `etherif.h`, with queue, callbacks, addresses, stats, and `Netif`.

## Control Flow

Attach parses an optional controller number and calls hardware attach. Walk/stat/open/read/write mostly delegate to `netif`. `etheriq` receives frames, filters multicast/promiscuous/destination matches, fans packets out to matching `Netfile`s, supports bridge/headersonly tracing, and frees or returns the input block. `etheroq` handles outbound frames, loops back local/broadcast/promiscuous packets, queues non-loopback frames, and calls the hardware transmit callback.

`etherreset` reads `etherN` config, matches registered cards, applies configured `ea=`, invokes hardware reset, wires interrupts, initializes `netif` and output queue, and prints device info. `ethercrc` computes Ethernet multicast CRC.

## Dependencies

Depends on `netif`, `etherif.h`, `Block` queues, `intrenable`, `isaconfig`, and hardware drivers such as `etherfcc.c` or `ethersaturn.c`.

## Risks

Packet fanout can allocate copies per consumer and increment overflow counters on failure. Hardware callback correctness is assumed. `parseether` accepts fixed two-hex-digit bytes and does limited validation.
