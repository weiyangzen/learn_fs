# File Research: sources/os/plan9/plan9/sys/src/9/mtx/etherif.h

## Role

MTX Ethernet driver interface header. It defines the shared `Ether` structure and registration/helper prototypes used between generic Ethernet code and hardware drivers.

This is network interface glue, not filesystem code.

## Main Contents

- Queue/descriptor constants:
  - `Nrdre`
  - `Ntdre`
  - `Nrb`
- `Ether` structure:
  - hardware identity and bus fields
  - MAC address
  - interface name
  - receive/transmit callback hooks
  - multicast/promiscuous hooks
  - controller-private pointer
  - `Netif` embedded state
- Prototypes:
  - `etheriq`
  - `addethercard`
  - `ethercrc`
- Ring helpers:
  - `NEXT`
  - `PREV`

## Important Behavior

- Provides the contract consumed by `devether.c` and `ether2114x.c`.

## Dependencies And Assumptions

- Assumes `Netif`, `Block`, and Plan 9 network structures are visible to including files.

## Notable Risks

- Fixed RX/TX ring sizes are global defaults for drivers using this interface.
