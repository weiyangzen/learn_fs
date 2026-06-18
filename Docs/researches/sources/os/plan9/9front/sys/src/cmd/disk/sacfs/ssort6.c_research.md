# File Research: sources/os/plan9/9front/sys/src/cmd/disk/sacfs/ssort6.c

## Purpose
Implements suffix-array sorting primitives used to compute the Burrows-Wheeler transform for SAC compression.

## Key Behavior
- `ssort()` sorts integer sequences with dense alphabets, using bucket labeling, iterative doubling, and optional shared-prefix interval tracking.
- `ssortbyte()` specializes suffix sorting for byte buffers, bucketed by two-byte prefixes and with a unique end-of-string marker lower than all input bytes.
- Returns the identity permutation index used by the compressor as the BWT primary index.
- Uses `BUCK` high-bit markers to represent unresolved buckets during iterative refinement.
- `ssortit()` repeatedly refines buckets using successor labels at increasing offsets until all suffixes are ordered.
- Optional shared-length support uses `lift()` and `sharedlen()` with a compact auxiliary tree.
- Includes a custom quicksort/insertion-sort hybrid (`qsort2`) specialized for sorting permutation entries by successor label, with median-of-three/pseudomedian pivoting.

## Interfaces And Dependencies
- Exports `ssort()` and `ssortbyte()` declared in `ssort.h`.
- Operates on caller-supplied arrays for output permutation and optional shared-length data.

## Notes
This is performance-oriented compression support code rather than a general library; several error returns indicate bad input alphabet shape or allocation failure.
