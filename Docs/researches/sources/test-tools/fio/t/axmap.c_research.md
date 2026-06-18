# sources/test-tools/fio/t/axmap.c

## Purpose
`t/axmap.c` is a standalone executable test for fio's `axmap` bit map and LFSR interaction. It validates bit setting, duplicate detection, multi-bit set behavior, overlap handling, and `axmap_next_free()` wraparound/full-map behavior.

## Important APIs, Types, And Functions
The tests call `lfsr_init()`, `lfsr_next()`, `axmap_new()`, `axmap_free()`, `axmap_set()`, `axmap_isset()`, `axmap_set_nr()`, and `axmap_next_free()`. Test functions are `test_regular()`, `check_next_free()`, `test_next_free()`, `test_multi()`, `test_overlap()`, and `main()`. `struct overlap_test` defines table-driven expected return values for overlapping range sets.

## Control Flow
`main()` accepts optional map size and seed, then runs regular single-bit coverage, multi-bit range tests at offsets 0 and 17, overlap table tests, next-free tests at the chosen size, and two additional next-free stress cases sized to exercise deeper axmap levels. It returns distinct nonzero codes for each failing phase.

## State And Persistence Behavior
Each test creates a fresh `struct axmap`, mutates bits, prints progress to stdout, and frees the map. There is no persistent state. The LFSR seed controls deterministic pseudo-random traversal for repeatability.

## Dependencies And Integration Points
The file depends on fio's `lib/lfsr.h` and `lib/axmap.h`. It is a direct test signal for allocator/map code used by fio random offset selection and other bit-tracking logic.

## Risks And Edge Cases
There appears to be a suspicious check in `test_multi()` using `axmap_isset(map, val + i)` inside a loop where `i` already ranges from `val` to `val + 127`, which tests `2 * val` onward for nonzero offsets rather than the intended range. Default `size` is cast to `unsigned int map_size` in `test_multi()`, so very large user-provided sizes can truncate. Some loops use `int i` for values derived from `uint64_t size`, which can be unsafe for huge inputs.

## Test Signals
Expected successful output is each phase printing `pass!` or table rows marked `PASS`, with process exit 0. Failures identify duplicate bits, missing set bits, short LFSR loops, incorrect `set_nr()` counts, incorrect next-free values, full-map handling failures, or out-of-bounds next-free behavior.
