# File Research: sources/os/bsd/freebsd-src/sbin/routed/radix.h

Radix tree public structures, macros, and function declarations for the userland routing table implementation.

Key responsibilities:
- Defines `struct radix_node` for internal and leaf nodes with parent, bit index, bit mask, flags, key, mask, and duplicate-key chain fields.
- Defines `struct radix_mask` for masks attached to subtrees and normal-route annotations.
- Defines `struct radix_node_head` with tree root, key sizes, operation callbacks, and embedded root nodes.
- Provides mask allocation/free-list macros and memory wrapper macros.
- Declares `rn_init()`, `rn_inithead()`, and `rn_walktree()`.

Dependencies:
- Includes `sys/cdefs.h`; expects `rtmalloc`, `free`, `memmove`, and `memset` availability through including translation units.

Notable risks:
- Exposes internal layout used by route entries and tree manipulation code; ABI/layout changes must match `radix.c`.
- Allocation macros rely on a global free list and have side effects, so callers must treat them carefully.
