# File Research: sources/os/plan9/plan9/sys/src/cmd/vi/mem.c

Purpose: Simulated memory/TLB/page mapping for the MIPS interpreter.

Key behavior:
- `ifetch` validates alignment, updates icache/profile counters, maps the page, and fetches big-endian instructions.
- Provides aligned and byte/half/word memory read/write helpers with breakpoint checks.
- `memio` copies strings/buffers between simulated and host memory.
- `dotlb` simulates a random-replacement TLB.
- `vaddr1` lazily maps text/data pages from the executable and zero-fills bss/stack pages.
- `vaddr` traps on unmapped addresses; `badvaddr` checks alignment and mapping.

Dependencies:
- Uses segment metadata from `mips.h`, executable fd `text`, profiler array, random functions, and longjmp-based traps.

Notable details:
- Memory is modeled as page tables per segment, with pages allocated on first touch.
