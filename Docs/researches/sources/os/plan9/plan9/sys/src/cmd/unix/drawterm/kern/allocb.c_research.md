# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/allocb.c

Plan 9 `Block` allocator for packet/queue buffers in drawterm’s kernel facade.

Key responsibilities:
- Allocates aligned `Block` structures with header slack (`Hdrspc`) for protocol headers.
- Provides process-context `allocb()` and interrupt-time `iallocb()` allocation paths.
- Tracks interrupt allocation usage against `conf.ialloc`.
- Frees blocks, honors custom block free callbacks, updates interrupt allocation accounting, and poisons freed blocks with a sentinel.
- Provides `checkb()` sanity validation and `iallocsummary()` reporting.

Important behavior:
- `allocb()` panics if called without `up`.
- `iallocb()` returns nil when allocation exceeds the configured interrupt allocation budget.
- Data pointers are aligned to `BLOCKALIGN`.

Notable risks:
- Allocation failure generally panics in process context.
- Poisoning uses a fixed invalid pointer value; diagnostics are helpful but not memory-safe if stale users dereference before checks.
