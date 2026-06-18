# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/acidleak.c

This file implements `acidleak`, a Plan 9 auxiliary tool that reads heap/block tracing records from stdin and reports unreachable allocated blocks or emits a memory-map bitmap.

Key behavior:
- Parses `data`, `block`, `free`, and `range alloc` input records into growable arrays.
- Sorts blocks and data words by address, then marks reachable allocation blocks by following pointer-like values through heap headers.
- Treats candidate pointers as block starts at `value - 8` or `value - 16`, guessing common allocator header sizes.
- In text mode, prints unmarked non-free blocks as leak candidates.
- With `-b`, emits an `m8` bitmap where colors distinguish allocated, free, header, leaked, and leaked-header regions.
- Supports `-r` bitmap resolution and `-x` bitmap width.

Important details:
- `Block` records keep address, size, two header words, optional labels, mark/free flags, and first data pointer.
- `Data` records track source address, value, type, and owning block.
- Reachability is recursive through `markblock()`.
- Input trust is high; malformed or inconsistent traces can trigger assertions.

Filesystem relevance:
- Indirect: diagnostic utility for Plan 9 process/memory debugging, not filesystem implementation code.
