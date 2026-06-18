# File Research: sources/os/plan9/9front/sys/src/9/port/allocb.c

Network/block buffer allocation helpers for kernel `Block` objects.

Key behavior:
- `_allocb` allocates a `Block` plus headroom, tailroom, and alignment padding, aligns the data area, and initializes read/write pointers with header space reserved.
- `allocb` is process-context allocation that waits for memory and panics if called in interrupt/locked context without memory.
- `iallocb` is interrupt-safe allocation that returns nil on failure, rate-limits warnings, and eventually panics after excessive repeated failures.
- `freeb` returns pooled blocks to their `Bpool` freelist or poisons fields with `Bdead` before freeing ordinary blocks.
- `_alignment` rounds pool alignment to a power of two at least `BLOCKALIGN`.
- `iallocbp` allocates from a `Bpool` freelist or creates a new aligned block for that pool.
- `growbp` preallocates a batch of `Block` headers and backing storage for a `Bpool`.
- `checkb` validates block pointer fields and panics on poisoned or out-of-range buffers.

Notable dependencies:
- Kernel heap allocation, `Block`, `Bpool`, and block flags from shared port data.
- Interrupt locks for pool freelists.

Research notes:
- Blocks reserve 64 bytes of headroom and 16 bytes of trailer space by default.
- Pooled blocks are reset to `BINTR` on free and reuse, reflecting interrupt-safe network use.
