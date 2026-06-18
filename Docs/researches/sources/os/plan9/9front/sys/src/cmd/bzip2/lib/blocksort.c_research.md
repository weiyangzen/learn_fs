# File Research: sources/os/plan9/9front/sys/src/cmd/bzip2/lib/blocksort.c

This is libbzip2’s Burrows-Wheeler block sorting implementation.

Major responsibilities:
- Provides `BZ2_blockSort(EState *s)`.
- Uses a fast main sorting path for normal blocks.
- Falls back to a slower but robust sorting path for repetitive data or small blocks.
- Determines `origPtr`, the BWT primary index.

Algorithms:
- `fallbackSort` uses initial byte radix sorting and iterative bucket refinement similar to suffix-array construction.
- `mainSort` uses two-byte bucket sorting, running-order scheduling, 3-way string quicksort, quadrant hints, and budget accounting.
- `mainGtU`, `mainSimpleSort`, and `mainQSort3` perform suffix comparisons and sorting within buckets.
- If work budget is exhausted, `BZ2_blockSort` reruns fallback sorting.

Notable implementation details:
- The file is performance-oriented and macro-heavy.
- `block` overshoot and `quadrant` arrays are tightly laid out inside compression work buffers.
- Sorting output is in `s->ptr`/`s->arr1`.

Risks and caveats:
- Relies on internal buffer alignment and `BZ_N_OVERSHOOT`.
- Uses explicit stack arrays for quicksort recursion simulation.
- Derived from upstream bzip2 1.0-era code.
