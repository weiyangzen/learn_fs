# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/mem.c

## Scope

Guest memory and lazy segment paging for `5i`.

## Behavior

- Fetches instructions and reads/writes guest bytes, halfwords, words, and 64-bit values in ARM little-endian order.
- Enforces alignment for instruction fetches and stores; unaligned reads emulate ARM rotation behavior.
- `memio()` copies between host buffers and guest memory, including bounded string reads.
- `dotlb()` maintains simple random-replacement TLB hit/miss stats.
- `vaddr()` maps guest addresses to lazily allocated pages backed by executable text/data or zeroed bss/stack.

## Dependencies

Uses segment setup from `5i.c`, profiling array `iprof`, breakpoint checks, and global `text` file descriptor.

## Risks And Invariants

- `ifetch()` indexes `iprof[(addr-textbase)/PROFGRAN]` without segment-bound checks before `vaddr()` validation.
- Data page partial-read zeroing assumes `foff + n > fileend` captures the final data page case.
- Guest memory faults longjmp to debugger rather than returning errors.
