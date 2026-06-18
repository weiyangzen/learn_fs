# File Research: sources/os/plan9/9front/sys/src/cmd/ki/mem.c

Memory access layer for `ki`. `ifetch` enforces instruction alignment, triggers icache hooks, profiles text addresses, and fetches big-endian 32-bit instructions. Data accessors provide byte, halfword, word, and vlong reads/writes with SPARC big-endian layout and alignment checks.

`memio` copies between simulated memory and host buffers for syscall emulation, including bounded string reads. `vaddr` translates simulated virtual addresses into lazily allocated segment pages, loading text/data from the executable via `pread` and zero-filling bss/stack. Invalid addresses raise simulated MMU misses through the debugger error path.
