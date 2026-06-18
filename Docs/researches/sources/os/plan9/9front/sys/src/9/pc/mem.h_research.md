# File Research: sources/os/plan9/9front/sys/src/9/pc/mem.h

## Purpose
Defines fundamental 32-bit x86 memory, virtual-address, segment, selector, and page-table constants for C and assembly.

## Key Elements
Declares page/word sizes, alignment macros, `MAXMACH`, `KSTACK`, clock constants, kernel/user virtual layout (`KZERO`, `KTZERO`, `VPT`, `KMAP`, `VMAP`, `USTKTOP`), fixed bootstrap physical/virtual addresses (`CONFADDR`, `CPU0PDB`, `CPU0PTE*`, `CPU0GDT`, `MACHADDR`, `CPU0MACH`), boot argument locations, GDT segment indexes/selectors, segment descriptor flags, virtual MMU sizing, PTE flags, page-directory/table index macros, and PAT write-combining index.

## Dependencies
Included by both C and assembly sources; values are consumed directly by `l.s`, MMU code, memory discovery, trap setup, and process/user entry code.

## Behavior/Risks
The comments note tight coupling: `ramscan` knows `CPU0END`, and `_startPADDR` assumes `CPU0PDB` is the first reserved page and that there are six reserved bootstrap pages. Changing these constants requires synchronized updates across boot assembly and memory management.
