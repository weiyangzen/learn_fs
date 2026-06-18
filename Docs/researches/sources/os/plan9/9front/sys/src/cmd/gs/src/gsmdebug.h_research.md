# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsmdebug.h

Allocator debugging definitions.

Key behavior:
- Declares debug fill pattern bytes:
  - allocated-but-uninitialized
  - locally allocated block
  - garbage collected
  - locally deleted block
  - freed
- Defines `gs_alloc_debug` as `gs_debug['@']`.
- Declares `gs_alloc_memset`.
- Defines `gs_alloc_fill`; under `DEBUG`, it fills memory only when allocator debug flag is set, otherwise it is a no-op.

Dependencies:
- Requires `gdebug.h` for `gs_debug`.

Research notes:
- Fill constants are defined in `gsmemory.c`.
- Used by allocators and no-GC string free lists to catch use-after-free/uninitialized memory during debug runs.
