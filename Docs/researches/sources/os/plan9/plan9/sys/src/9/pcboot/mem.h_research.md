# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/mem.h

## Purpose
Shared memory layout, paging, segmentation, and bootstrap address constants for C and assembly.

## Main Interfaces
- Defines page/word sizes, `KZERO`, `KSEGM`, virtual regions, stack sizes, low-memory fixed buffers, boot kernel/decompression addresses, memory scan limits, segment selectors, descriptor flags, PTE flags, and paging index macros.
- Defines constants such as `CONFADDR`, `BIOSXCHG`, `BIOSTABLES`, `Bootkernaddr`, `Unzipbuf`, `Mallocbase`, `MemMin`, `MemMax`, `Kernelmax`, and `LOWPTEPAGES`.

## Implementation Notes
- Reserves the bottom 64 KiB for real-mode return paths and fixed exchange structures.
- Merges `MACHADDR` and `CPU0MACH` because the bootstrap only uses one processor.
- Maps the boot decompressor and kernel staging areas at fixed physical addresses.
- Declares GDT selector layout used by all assembly stages.
- Provides page-directory/page-table index macros used by C and assembler.

## Dependencies And Risks
- Comments explicitly state some invariants, such as `PDX(TMPADDR) == PDX(MACHADDR)`.
- Constants must match loaded-kernel expectations for `CONFADDR`.
- Assembly files depend directly on selector and address values.
