# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zarray.c

This file implements the core PostScript array creation and stack transfer operators.

Key behavior:
- `array` allocates a writable array of the requested integer size and initializes entries to null.
- `aload` expands an array or packed array onto the operand stack and leaves the source array on top.
- `astore` stores stack objects into a writable array, including the slow path for stack segments that cross ref-stack boundaries.
- Generic array-like operators such as `copy`, `get`, `put`, `length`, `forall`, and interval operations are intentionally implemented elsewhere in `zgeneric.c`.

Important dependencies:
- Uses Ghostscript allocator APIs from `ialloc.h`.
- Handles packed arrays via `ipacked.h`.
- Uses `ref_stack_push`, `ref_stack_store`, and `refcpy_to_old` to preserve VM/write-barrier behavior.

Registered operators:
- `aload`
- `array`
- `astore`
