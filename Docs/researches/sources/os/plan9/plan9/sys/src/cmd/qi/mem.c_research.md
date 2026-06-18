# File Research: sources/os/plan9/plan9/sys/src/cmd/qi/mem.c

Simulated memory subsystem for `qi`.

Key responsibilities:
- Fetches big-endian instructions with alignment checks and per-PC profiling.
- Provides big-endian byte, halfword, word, and doubleword memory accessors.
- Performs alignment checks for word/half/doubleword accesses.
- Triggers memory breakpoints on reads and writes.
- Provides `memio()` for copying between host buffers and simulated memory, including NUL-terminated strings.
- Lazily maps virtual addresses to per-segment page buffers.
- Loads text/data pages from the executable and allocates zeroed BSS/stack pages.

Dependencies:
- Uses `Memory`, `Segment`, breakpoint state, profiler arrays, executable fd `text`, and constants from `power.h`.

Notable risks:
- Address misses longjmp back to the debugger rather than returning errors.
- Segment tables are lazy and page-sized; file offset calculations must match `qi.c` layout.
- Doubleword alignment check only tests word alignment, matching the source comment uncertainty.
