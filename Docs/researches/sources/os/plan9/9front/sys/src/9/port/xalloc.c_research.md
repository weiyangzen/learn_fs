# File Research: sources/os/plan9/9front/sys/src/9/port/xalloc.c

Early/kernel physical memory allocator for machine-addressable kernel memory.

Key responsibilities:
- Initializes a fixed hole descriptor pool and populates allocatable kernel memory holes from `conf.mem` after reserving user pages.
- Allocates zeroed or unzeroed blocks from a sorted free-hole list with a small header containing size and magic.
- Frees allocations by validating the magic header and returning physical ranges to the hole list.
- Merges adjacent free holes in `xhole()` and exposes `xsummary()` diagnostics.
- Provides `xspanalloc()` for allocations constrained by alignment/span, returning unused leading/trailing fragments to the free list.
- Provides `xmerge()` to coalesce adjacent allocated blocks when possible.

Dependencies:
- Uses architecture `KADDR`, `PADDR`, and `cankaddr()` constraints plus global memory configuration.

Notable behavior:
- The allocator refuses to use physical memory that cannot be reached through `KADDR()`.
- If the fixed hole table is exhausted, returned memory is leaked with a diagnostic rather than corrupting the free list.
