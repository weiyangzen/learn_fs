# File Research: sources/os/plan9/9front/sys/src/9/ppc/lblast.h

Assembly include for Blast board support.

Key responsibilities:
- Defines cached/uncached BAT mappings and low-level constants for Blast memory and I/O regions.
- Provides assembler-visible address, cache, and TLB constants used by PowerPC startup/low-level code.

Dependencies:
- Complements `blast.h` and `mem.h` for assembly consumers.
