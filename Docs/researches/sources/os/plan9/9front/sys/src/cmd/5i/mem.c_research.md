# File Research: sources/os/plan9/9front/sys/src/cmd/5i/mem.c

This file implements instruction fetch, memory loads/stores, debugger memory I/O, simulated TLB, and lazy paging for `5i`.

Instruction and data access:
- `ifetch()` enforces word-aligned instruction fetch, updates I-cache/profiling, translates address, and returns little-endian 32-bit instruction word.
- `getmem_4()` and `getmem_2()` assemble multi-byte values through byte reads.
- `getmem_w()` handles unaligned word reads by rotating the aligned word, checks read breakpoints, and returns little-endian words.
- `getmem_h()` handles unaligned halfword reads similarly, checks read breakpoints, and returns halfwords.
- `getmem_b()` reads a byte and checks read breakpoints.
- `getmem_v()` returns a 64-bit value from two words.
- `putmem_h()`, `putmem_w()`, `putmem_b()`, and `putmem_v()` write little-endian values and check write breakpoints; halfword/word stores reject unaligned addresses.
- `memio()` copies between debugger buffers and simulated memory, including bounded C-string reads.

TLB and paging:
- `dotlb()` tracks simulated page hits/misses and randomly replaces a TLB entry.
- `vaddr()` translates a virtual address to a lazily allocated page:
  - text pages are read from executable text offset,
  - data pages are read from executable data offset and zero-filled past file data,
  - BSS and stack pages are zero-allocated.
- On unmapped address, reports user TLB miss and longjmps to command loop.

Dependencies and interactions:
- Uses `memory.seg[]` laid out by `5i.c:initmap()`.
- Breakpoint checks go through `brkchk()`.
- Command shell and instruction execution use these accessors.

Research relevance:
- Core simulated memory subsystem for `5i`.

Risk notes:
- `getmem_4()`/`getmem_2()` assemble via byte reads while `getmem_w()`/`getmem_h()` have special unaligned behavior; callers need the right accessor.
- Lazy text/data reads operate page-at-a-time and assume file offsets derived in `initmap()`.
- TLB replacement uses `lnrand()` and only models statistics, not permissions.
