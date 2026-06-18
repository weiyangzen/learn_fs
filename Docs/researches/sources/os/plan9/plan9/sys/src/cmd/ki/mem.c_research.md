# File Research: sources/os/plan9/plan9/sys/src/cmd/ki/mem.c

This file implements instruction fetch, data memory access, user/kernel memory copy, and lazy virtual address translation for `ki`.

`ifetch()` enforces instruction alignment, updates the optional icache, resolves the page with `vaddr()`, increments instruction profile counters, and returns a big-endian 32-bit instruction. `getmem_*()` and `putmem_*()` implement big-endian byte/halfword/word access with alignment traps and memory breakpoint checks.

`memio()` copies between emulator memory and host buffers for reads, writes, and NUL-terminated strings with a maximum size. It is heavily used by syscall emulation.

`vaddr()` resolves an address to a segment page, lazily allocates pages, loads Text/Data pages from the executable file, zero-fills Bss/Stack pages, tracks resident pages and references, and raises a simulated MMU miss on invalid addresses.
