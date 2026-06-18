# File Research: sources/os/plan9/plan9/sys/src/cmd/du.c

Plan 9 `du` implementation.

Key behavior:
- Recursively walks directories with `dirread()`, sums rounded file lengths, and prints totals.
- Options include all files, custom block size, floating output, warnings off, autoscale, byte mode, qid output, read-through mode, summary-only, mtime/atime output, and SI-prefix output selection.
- Uses a qid/type/dev cache to avoid directory cycles.
- `readflg` opens and reads file contents for every file without reporting normal totals.
- Uses Plan 9 `String` helpers to build child paths and quote-aware output formatting.

Filesystem relevance:
- User-level filesystem traversal and accounting utility; relies on qids to avoid loops.
