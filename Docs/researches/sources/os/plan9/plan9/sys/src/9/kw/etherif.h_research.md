# File Research: sources/os/plan9/plan9/sys/src/9/kw/etherif.h

## Purpose
Defines the common Ethernet controller interface used by the generic Ethernet device and hardware-specific drivers in this port.

## Key Contents
- `MaxEther = 2` and `Ntypes = 8`.
- `Ether` structure embedding `RWlock`, `ISAConf`, controller identity/configuration, MTU bounds, MAC address, callbacks, controller private pointer, output queue, link/full-duplex state, activity timestamp, and `Netif`.
- Controller callbacks include attach, close, detach, transmit, interrupt, ifstat, ctl, power, and shutdown.
- Declares `etheriq`, `addethercard`, `ethercrc`, and `parseether`.
- Defines circular ring helper macros `NEXT` and `PREV`.

## Dependencies and Integration
Shared by `devether.c`, `ether1116.c`, and other Ethernet controller drivers.

## Risks and Notes
The `Ether` structure is the ABI between generic netif-facing code and controller-specific code. Callback ownership and queue expectations must remain consistent.
