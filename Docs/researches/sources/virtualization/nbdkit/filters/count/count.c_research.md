# File Research: sources/virtualization/nbdkit/filters/count/count.c

Purpose: lightweight accounting filter for read/write/zero/trim byte totals.

Key details:
- Maintains atomic counters for bytes read, written, zeroed, and trimmed.
- Wraps `.pread`, `.pwrite`, `.trim`, and `.zero`, incrementing counters only after successful downstream operations.
- `.unload` logs final totals with `nbdkit_debug`.
- Falls back to non-atomic `_Atomic` macro on platforms without `<stdatomic.h>`.

Risk notes:
- On platforms without atomics, counters are explicitly “atomic enough” only for statistics, not strict concurrency accuracy.
