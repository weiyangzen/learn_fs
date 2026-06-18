# File Research: sources/os/plan9/plan9/sys/src/9/pc/ether8390.h

## Role

Header and x86-specific access layer for DP8390-compatible Ethernet drivers. It defines the shared controller state used by `ether8390.c` and board-specific drivers.

## Main Interfaces

- Defines `Dp8390`.
- Declares:
  - `dp8390reset(Ether*)`
  - `dp8390read(Dp8390*, void*, ulong, ulong)`
  - `dp8390getea(Ether*, uchar*)`
  - `dp8390setea(Ether*)`
- Defines register access macros `regr` and `regw`.
- Defines static data-port transfer helpers `rdread` and `rdwrite`.

## Data Structures

- `Dp8390` embeds a `Lock` and stores:
  - I/O register and data-port addresses.
  - Transfer width and shared-memory/dummy-read flags.
  - Receive and transmit page layout.
  - Transmit busy flag.
  - Multicast address-register shadow and 64 hash-bit reference counts.

## Important Behavior

- `rdread` and `rdwrite` select byte or word I/O transfer routines based on `ctlr->width`.
- Unsupported transfer widths panic.
- `Dp8390BufSz` defines the NIC page size as 256 bytes.

## Dependencies And Assumptions

- Assumes x86 I/O-port primitives `inb`, `outb`, `insb`, `outsb`, `inss`, and `outss`.
- Intended to be included after Plan 9 kernel and Ethernet definitions.
- Functions are static in the header because they are architecture/translation-unit local helpers.

## Notable Risks

- Header contains executable static functions, so changes affect every including board driver.
- Width must be initialized before any shared DP8390 code calls data-port helpers.
