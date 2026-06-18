# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/bitset.c

## Purpose

`bitset.c` implements dynamic kernel `bitset_t` storage and operations. It wraps bitmap macros with allocation, fanout support, atomic set/clear helpers, randomized selection, boolean set operations, matching, zeroing, and copying.

## Main Interfaces

Lifecycle and sizing: `bitset_init`, `bitset_init_fanout`, `bitset_fini`, `bitset_resize`, `bitset_capacity`.

Mutation and tests: `bitset_add`, `bitset_atomic_add`, `bitset_atomic_test_and_add`, `bitset_del`, `bitset_atomic_del`, `bitset_atomic_test_and_del`, `bitset_in_set`, `bitset_is_null`.

Search and algebra: `bitset_find`, `bitset_and`, `bitset_or`, `bitset_xor`, `bitset_match`, `bitset_zero`, `bitset_copy`.

## Behavior

`bitset_resize()` computes required words from `els << bs_fanout`, allocates zeroed storage, copies the overlapping old words, swaps storage, then frees the old array. Shrinking drops out-of-range elements.

Element positions are shifted by `bs_fanout`, allowing one logical element to map to spaced bitmap bits.

Atomic variants use bitmap atomic macros and return exclusive-test results for test-and-add/delete.

`bitset_find()` uses `CPU_PSEUDO_RANDOM()` to choose a starting word and rotate within words via `bitset_find_in_word()`, reducing bias toward low-order bits.

Boolean operations assume equal fanout and write into `res`, returning whether the result contains any set bits.

## Notable Invariants

- Callers must size the bitset before adding/removing elements.
- Add/delete assert the computed bit position is inside capacity.
- `bitset_find()` asserts `bs_words > 0`.
- Boolean operations assume compatible word counts; the code asserts only fanout equality.

## Dependencies

Uses `kmem_zalloc/free`, `bcopy`, `bzero`, bitmap macros, atomic bitmap macros, `lowbit()`, `CPU_PSEUDO_RANDOM()`, and kernel assertions.

## Research Notes

The main risks are caller-side capacity discipline, fanout overflow in `els << bs_fanout` or `elt << bs_fanout`, and ensuring result bitsets passed to boolean operations are at least as large as the operands.
