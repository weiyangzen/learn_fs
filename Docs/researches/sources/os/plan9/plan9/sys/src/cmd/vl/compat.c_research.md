# File Research: sources/os/plan9/plan9/sys/src/cmd/vl/compat.c

Purpose: Compatibility allocation and utility shims for the linker.

Key behavior:
- Replaces `malloc` with hunk-based allocation from linker-managed memory.
- `free` is a no-op.
- `calloc` allocates through the hunk allocator and zeroes memory.
- `realloc` is unsupported and aborts.
- `mysbrk` wraps `sbrk`.
- `setmalloctag` is a no-op.
- `fileexists` tests whether `stat` succeeds.

Dependencies:
- Uses linker globals `hunk`, `nhunk`, and `gethunk` from the linker core.

Notable details:
- Designed for linker lifetime allocation, not general-purpose memory management.
