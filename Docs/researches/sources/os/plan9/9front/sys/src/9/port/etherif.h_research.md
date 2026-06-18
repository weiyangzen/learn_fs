# File Research: sources/os/plan9/9front/sys/src/9/port/etherif.h

Defines the shared Ethernet controller interface. `Ether` embeds `ISAConf` and `Netif`, stores bus/device metadata, MTU bounds, device hooks for attach/transmit/control/power/shutdown, an output queue, MAC address, bridge MAC table, and optional destination MAC address table.

It declares helpers for speed/link updates, packet input, driver registration, Ethernet CRC, and MAC parsing. Small ring arithmetic macros are also provided.
