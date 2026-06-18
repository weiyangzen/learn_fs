# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/ktzero.s

## Purpose
Defines the `_KTZERO` text symbol used to expose the kernel text-zero address to C.

## Main Interfaces
- `TEXT _KTZERO(SB), $0`.

## Implementation Notes
- `dat.h` declares `extern void _KTZERO(void);` and defines `KTZERO` as the symbol address.
- The symbol acts as an address marker rather than executable logic.

## Dependencies And Risks
- Must link at the intended bootstrap text base for address calculations to be meaningful.
