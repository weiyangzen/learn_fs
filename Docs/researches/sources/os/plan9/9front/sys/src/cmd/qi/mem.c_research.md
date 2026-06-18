# File Research: sources/os/plan9/9front/sys/src/cmd/qi/mem.c

Virtual memory and memory access layer for `qi`.

Key responsibilities:
- `ifetch` fetches big-endian instructions, checks alignment, updates instruction profile counters, and optionally updates icache.
- `getmem_*` and `putmem_*` implement big-endian byte/halfword/word/vlong loads and stores with alignment checks.
- Memory breakpoints are checked on reads and writes.
- `memio` copies between host buffers and simulated memory for syscall argument/result handling.
- `vaddr` translates simulated virtual addresses to lazily allocated segment pages and demand-loads text/data from the executable.

Dependencies and coupling:
- Uses `memory.seg[]`, `text` fd, `textbase`, profile globals, `brkchk`, and `longjmp(errjmp)`.
- Segment definitions come from `qi.c:initmap`.

Filesystem/OS relevance:
- This is the simulator’s virtual memory subsystem, including lazy file-backed text/data paging and zero-backed bss/stack.
