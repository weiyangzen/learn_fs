# File Research: sources/os/plan9/plan9/sys/src/9/pc/mtrr.c

Memory Type Range Register support for configuring x86 cache attributes, especially write-combining framebuffer mappings.

Key elements:
- Defines MTRR MSR numbers, memory types, capability/default-type bit fields, and 36-bit physical sanity limit.
- `physmask` derives physical address width via extended CPUID and caps to 36 bits.
- `mtrrdec` and `mtrrenc` convert variable MTRR MSR base/mask pairs to/from base/size/type.
- `mtrrget`, `mtrrput` read/write indexed variable MTRRs.
- `mtrrop` performs synchronized all-CPU MTRR update: disables PGE, disables caching, disables MTRRs, writes register, restores defaults/cache state.
- `mtrrclock` lets other CPUs execute pending operations from the clock interrupt.
- `mtrr` validates alignment, type support, slot availability, posts the operation, and updates all CPUs.
- `mtrrprint` formats default and variable MTRR cache ranges.

Interactions:
- `screen.c` calls `mtrr(..., "wc")` for linear VGA framebuffers and tolerates failure.
- MP startup validates MTRR consistency across CPUs in `mp.c`.

Research notes:
- Critical for performance of memory-mapped video and possibly device regions.
- Slot selection reuses invalid entries, matching base/size entries, or entries above 4GB.
