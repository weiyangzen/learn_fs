# File Research: sources/teaching/xv6-public/mmu.h

x86 segmentation, paging, and trap-gate definitions.

Contents:
- EFLAGS and control register bits.
- Kernel/user segment selectors and descriptor counts.
- Segment descriptor structures and `SEG`/`SEG16` construction macros.
- DPL and segment type constants.
- Page directory/table index, address, size, rounding, and flag macros.
- `pte_t`, task state segment structure, gate descriptor structure, and `SETGATE`.

Role:
- Shared by assembly, VM, trap, process, and boot code.
- Encodes the low-level x86 protection and paging model used by xv6.
