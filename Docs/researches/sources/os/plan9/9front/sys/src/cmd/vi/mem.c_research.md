# File Research: sources/os/plan9/9front/sys/src/cmd/vi/mem.c

`mem.c` implements virtual memory access for the MIPS simulator. It validates alignment, fetches big-endian instructions and data, triggers memory breakpoints, copies syscall buffers, and demand-loads virtual pages from text/data files or zero-filled bss/stack segments.

`vaddr1()` walks simulator segments, updates a simple random-replacement TLB model when enabled, allocates pages on demand, and reads backing file bytes for text/data. `vaddr()` traps on unmapped access. `badvaddr()` is a non-trapping probe used for trace formatting.

This file is the simulated MMU and memory bus used by instruction execution and syscall emulation.
