# File Research: sources/os/plan9/plan9/sys/src/9/pc/etherif.h

## Purpose

Shared Plan 9 PC Ethernet interface header. It defines the per-device `Ether` structure used by `devether.c` and many PC Ethernet drivers, plus common helper declarations and ring-index macros.

## Contents

- Constants:
  - `MaxEther = 48`: maximum registered Ethernet card types.
  - `Ntypes = 8`: number of Ethernet protocol type slots in the embedded `Netif`.
- Forward declaration:
  - `typedef struct Ether Ether;`
- `struct Ether`:
  - Embeds `ISAConf` for hardware configuration.
  - Tracks controller number, PCI/TBDF identifier, and Ethernet address.
  - Provides driver callbacks:
    - `attach`
    - `detach`
    - `transmit`
    - `interrupt`
    - `ifstat`
    - `ctl`
    - `power`
    - `shutdown`
  - Holds driver-private controller pointer `ctlr`.
  - Holds output queue `oq`.
  - Embeds `Netif`, making the generic network-interface state part of every Ethernet device.
- Shared functions:
  - `etheriq(Ether*, Block*, int)`: input packet demultiplexing path.
  - `addethercard(char*, int(*)(Ether*))`: register a card reset/probe routine.
  - `ethercrc(uchar*, int)`: Ethernet CRC helper.
  - `parseether(uchar*, char*)`: parse textual Ethernet address.
- Ring macros:
  - `NEXT(x, l)` wraps an index forward modulo length.
  - `PREV(x, l)` wraps an index backward modulo length.

## Integration

This header is included by the generic Ethernet device implementation `devether.c` and by many PC Ethernet drivers such as `etherga620.c`, `ether82557.c`, `ether8169.c`, `ether2114x.c`, `ether8390.c`, and others.

The generic device layer uses `addethercard` to build the available driver table and allocates/populates `Ether` instances during probing. Individual drivers fill the callback fields during reset/probe so the generic `/net/ether*` interface can call into device-specific attach, transmit, interrupt, statistics, control, power, and shutdown paths.

## Dependencies

The header assumes surrounding Plan 9 kernel headers have already defined:

- `ISAConf`
- `uchar`
- `Eaddrlen`
- `Ureg`
- `Queue`
- `Netif`
- `Block`
- `ulong`

It has no include guard, which is common in this older Plan 9 kernel style but means it should be included once per compilation unit.

## Filesystem Relevance

Indirect. This is networking infrastructure in the Plan 9 kernel PC port. It does not implement VFS or local filesystem operations, but it is part of the OS kernel source tree covered by subset A.

## Risks and Maintenance Notes

- `Ether` is a shared ABI-like structure across all PC Ethernet drivers and `devether.c`; field changes have broad driver impact.
- Callback nullability is driver-dependent, so callers must continue to honor the existing conventions.
- `NEXT` and `PREV` evaluate their arguments directly; callers should avoid side-effect expressions.
- The embedded `Netif` means generic network state and driver state are tightly coupled.

## Verification Notes

- Full file size checked: 35 lines, 846 bytes.
- SHA-256: `4053549ec24e0abdf72289bb6d664630c9fbe493678e242e1c9651a9c3bd6b65`.
