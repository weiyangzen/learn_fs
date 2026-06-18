# File Research: sources/os/plan9/plan9/sys/src/cmd/bzip2/lib/blocksort.c

Core Burrows-Wheeler block sorting machinery from libbzip2 1.0.

Contains two sorting paths:

- Main sort for normal blocks: two-byte radix bucket setup, Sedgewick/Bentley 3-way string quicksort, quadrant descriptors, bucket scanning, and a work budget.
- Fallback sort for highly repetitive or small blocks: initial one-character radix sort followed by exponential bucket refinement inspired by Manber-Myers suffix-array construction.

Key public entry point:

- `BZ2_blockSort(EState *s)`: sorts block rotations into `s->ptr`/`arr1`, chooses main or fallback sort, and records `s->origPtr`.

The work-factor budget controls when the main sort gives up and falls back. The implementation is performance-critical and heavily macro/inline optimized.
