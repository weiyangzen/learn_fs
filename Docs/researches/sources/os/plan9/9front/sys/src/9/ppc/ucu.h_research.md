# File Research: sources/os/plan9/9front/sys/src/9/ppc/ucu.h

Small PPC platform memory/MMU header for a Saturn-based target. It defines flash/DRAM/plan9.ini locations, the `Saturn` MMIO base, `TLBENTRIES`, and PTE policy bits used by fault/MMU code.

The file sets `MEM1SIZE` to 32 MiB, disables a second memory bank, and defines cache/write policy defaults: `PTEVALID` as write-through/memory-coherent bits, writable and read-only encodings, and cached/uncached selectors.
