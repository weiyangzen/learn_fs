# File Research: sources/os/plan9/plan9/sys/src/9/ppc/io.h

## Role

Defines generic bus type encodings and helpers for PPC kernel device identifiers.

## Main Definitions

Enumerates bus types including ISA, PCI, PCMCIA, VME, and `BusPPC`. Defines `MKBUS(t,b,d,f)` to pack type, bus, device, and function into a `tbdf`, with extractors `BUSFNO`, `BUSDNO`, `BUSBNO`, `BUSTYPE`, `BUSBDF`, and sentinel `BUSUNKNOWN`.

## Dependencies

Used by device configuration and drivers such as Ethernet to tag controller bus identity.

## Risks

The bit layout is shared convention. Incorrect packing/extraction would break PCI/device matching and printed hardware identity.
