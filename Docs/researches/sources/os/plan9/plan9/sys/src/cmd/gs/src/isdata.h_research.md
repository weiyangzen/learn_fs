# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/isdata.h

Purpose: defines shared data structures for expandable stacks of Ghostscript refs.

Key design:
- Stack blocks include guard elements at top and bottom for low-overhead overflow/underflow detection.
- GC safety requires unused block areas to contain legitimate refs, so allocation, block transitions, and GC cleanup explicitly null unused slots.
- `ref_stack_t` stores mutable stack pointers, current block ref, extension sizes, max-stack parameter, margin/body sizing, initialization parameters, and allocator.

The header defines `s_ptr` aliases, opaque `gs_ref_memory_t`, and the public GC descriptor macro for `ref_stack_t`.
