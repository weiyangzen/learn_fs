# File Research: sources/os/bsd/freebsd-src/sys/sys/bitset.h

## Purpose
`bitset.h` implements fixed-size bitset operations as macros over structures containing a `__bits[]` long array.

## Main Interfaces
- Primitive operations include clear, set, test, zero, fill, set-of-one, copy, compare, subset, overlap, count, first-set, first-set-at, first-last-set, and foreach iteration.
- Set algebra includes AND, ANDNOT, OR, ORNOT, XOR, and two-source variants.
- Atomic forms include bit set/clear, test-and-set/clear, OR/AND updates, acquire variants, and release copy stores.
- Public `BIT_*` aliases are enabled for `_KERNEL` or `_WANT_FREEBSD_BITSET`.
- Kernel allocation helpers `BITSET_ALLOC` and `BITSET_FREE` wrap `malloc`/`free` with `BITSET_SIZE`.

## Implementation Notes
The header optimizes single-word constant-size bitsets through `__constexpr_cond`, avoiding division/modulo when the compiler can prove one word. Iteration uses a local word cache and `ffsl()` so it can traverse set or clear bits non-destructively. Atomic operations operate word-by-word and rely on `atomic_*_long` semantics.

## Dependencies and Constraints
The consuming bitset type must define `__bits[]`, and the environment must provide `_BITSET_BITS` and `__bitset_words()`. Atomic macros require machine atomic support. Full-set checks compare all backing words to all-ones and do not mask unused high bits in the last word.
