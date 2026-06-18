# File Research: sources/local-fs/e2fsprogs/e2fsck/mtrace.awk

## Purpose
AWK post-processor for allocation traces emitted by `mtrace.c`.

## Main Behavior
- `+ addr size`: records allocation, reports duplicate allocation at same address.
- `- addr`: clears allocation, reports freeing an address that was never allocated.
- `< addr`: old pointer side of realloc, clears prior allocation or reports missing prior allocation.
- `> addr size`: new pointer side of realloc, records allocation or reports duplicate.
- Ignores start markers `=` and failed realloc markers `!`.
- At `END`, prints allocations still outstanding.

## Integration
Used only with optional `MTRACE` debugging support.

## Risks / Notes
The script sets array entries to empty strings instead of deleting them, then filters nonempty entries at end.
