# File Research: sources/os/plan9/plan9/sys/src/9/kw/arm.s

## Purpose
Provides shared ARM assembly macros and constants for the SheevaPlug/Kirkwood ARM926EJ-S port.

## Key Contents
- Address translation macros `PADDR`, `KADDR`, and L1 page-table index `L1X`.
- PTE template constants for DRAM and I/O sections.
- `PUTC` debug-output macro writing to `PHYSCONS`.
- `CLZ` instruction encoding macro.
- Barrier macros:
  - `DMB`: data memory barrier using CP15.
  - `DSB`: drain/write-buffer/data synchronization barrier.
  - `ISB`: instruction prefetch flush.
  - `BARRIERS`: combined ISB and DSB.
- Page-table fill/zero macros `FILLPTE` and `ZEROPTE`.

## Dependencies and Integration
Included by low-level assembly files needing memory barriers, page-table construction, early console output, and ARM CP15 encodings from `arm.h`.

## Risks and Notes
The barrier implementation is ARM926/Sheeva-specific and uses CP15 cache operations rather than newer architectural barrier mnemonics.
