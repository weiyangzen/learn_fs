# File Research: sources/teaching/xv6-riscv/kernel/kalloc.c

Implements the kernel physical page allocator.

Important behavior:
- `kinit()` initializes a spinlock and frees physical pages from kernel `end` to `PHYSTOP`.
- `freerange()` rounds the start up to a page boundary and frees each page.
- `kfree()` validates page alignment/range, fills freed memory with junk, and pushes it onto the freelist.
- `kalloc()` pops one page from the freelist and fills allocated memory with junk.

Filesystem relevance: supports page allocations for page tables, process trapframes/stacks, pipe buffers, virtio rings, and lazy user pages. It underpins memory needed by filesystem-facing syscalls such as `pipe`, `exec`, and `sbrk`.
