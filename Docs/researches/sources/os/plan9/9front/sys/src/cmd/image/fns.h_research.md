# File Research: sources/os/plan9/9front/sys/src/cmd/image/fns.h

Declares shared helper functions for the Plan 9 image commands in this group.

Key points:
- Declares row-work splitting, checked memory allocation, checked `Memimage` allocation/read/write, checked display `Image` allocation, and `Memimage` to `Image` conversion.
- Used by `affinewarp.c`, `correlate.c`, `histogram.c`, and `util.c`.

Dependencies and interactions:
- Types come from Plan 9 draw and memdraw headers.

Research relevance:
- Small shared interface for robust image command helpers.
