# File Research: sources/os/plan9/plan9/sys/src/9/mtx/devether.c

## Role

Generic Ethernet network device frontend for the MTX port. It exposes Ethernet interfaces through Plan 9 device files and dispatches to registered hardware drivers such as `ether2114x`.

This is network device infrastructure, not filesystem code.

## Main Interfaces

- Device operations:
  - `etherattach`, `etherwalk`, `etherstat`, `etheropen`, `etherclose`
  - `etherread`, `etherbread`, `etherwrite`, `etherbwrite`
- Packet queues:
  - `etheriq`
  - `etheroq`
- Driver registration and setup:
  - `addethercard`
  - `etherreset`
- Utilities:
  - `parseether`
  - `ethercrc`

## Important Behavior

- Uses the Plan 9 `netif` framework for clone/data/control/stats files.
- `etheriq` dispatches received packets to matching network files, supports promiscuous taps, and handles bridge input.
- `etheroq` pads short frames, updates output counters, and calls the hardware transmit function.
- `etherwrite` handles control writes separately from raw packet writes.
- `etherreset` attempts each registered card reset routine.
- `ethercrc` computes Ethernet CRC using polynomial `0xedb88320`.

## Dependencies And Assumptions

- Includes `../port/netif.h` and `etherif.h`.
- Hardware drivers register through `addethercard`.

## Notable Risks

- Packet fanout and promiscuous handling are shared across all Ethernet devices.
- Hardware driver reset order depends on static registration order.
