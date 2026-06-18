# File Research: sources/os/plan9/plan9/sys/src/9/ppc/etherif.h

## Role

Defines the PPC Ethernet controller interface shared by `devether.c` and hardware drivers.

## Main Definitions

`MaxEther` is 24 and `Ntypes` is 8. `Ether` embeds `ISAConf`, controller identity, MTU bounds, Ethernet address, hardware callbacks (`attach`, `transmit`, `interrupt`, `ifstat`, `ctl`), controller-private pointer, output queue, and `Netif`.

It declares `etheriq`, `addethercard`, and `ethercrc`, plus ring index macros `NEXT` and `PREV`.

## Risks

Hardware drivers are responsible for filling callbacks and `ctlr` consistently before registration. The queue and netif lifecycle is handled by `devether.c`, so drivers must not bypass those expectations.
