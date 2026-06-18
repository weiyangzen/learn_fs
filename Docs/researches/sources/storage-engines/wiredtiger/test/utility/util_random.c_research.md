# sources/storage-engines/wiredtiger/test/utility/util_random.c

## Purpose
`util_random.c` wraps WiredTiger's random number state for tests, giving callers simple random generation, deterministic seeding from a numeric seed, seeding one generator from another, and default seed creation with returned seed values for reproduction.

## Important APIs and functions
The exported functions are `testutil_random`, `testutil_random_from_random`, `testutil_random_from_seed`, and `testutil_random_init`. They operate on `WT_RAND_STATE` and seed pointers stored in `TEST_OPTS` by the option parser.

## Control flow and behavior
`testutil_random` uses the caller-provided state when available; otherwise it initializes a local state from WiredTiger's random initializer and returns one number. `testutil_random_from_random` advances a source generator and seeds the destination from that value. `testutil_random_from_seed` splits a 64-bit seed into lower and upper 32-bit halves and sets both internal generator components to nonzero values, borrowing from the other half when one half is zero. `testutil_random_init` generates a compact 24-bit seed when `*seedp` is zero, shifted by `n % 4` so multiple initializations close in time still diverge.

## State, dependencies, and integration
The functions mutate caller-owned `WT_RAND_STATE` and `uint64_t` seed storage. They depend on `__wt_random_init` and `__wt_random`, and are called by `parse_opts.c` to initialize data and extra random streams. Tests can print or pass `-PS` seeds to reproduce behavior.

## Risks and test signals
Risks include limited entropy for auto-generated seeds by design, repeated values if callers misuse the `n` index, and non-cryptographic random behavior. Signals include deterministic sequences from explicit seeds, distinct data/extra streams from default initialization, correct handling of seeds below `2^32`, and reproducible failure command lines including `TESTUTIL_SEED_FORMAT`.
