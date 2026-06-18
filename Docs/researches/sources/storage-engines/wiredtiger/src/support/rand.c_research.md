# sources/storage-engines/wiredtiger/src/support/rand.c

## Purpose
`rand.c` implements WiredTiger's fast pseudo-random number generation. It uses George Marsaglia's multiply-with-carry generator for 32-bit values, supports deterministic default seeding for skiplist behavior, session-specific random seeding, and Antithesis instrumentation override.

## Important APIs, Types, and Functions
`__wt_random_init_default` initializes a `WT_RAND_STATE` to fixed default seeds. `__wt_random_init_seed` mixes a caller-provided 64-bit seed into the state using circular shifts. `__wt_session_rng_init_once` initializes per-session RNGs on first use: `rnd_skiplist` with the default seed and `rnd_random` with session id, clock, and process id. `__wt_random` produces a 32-bit value and repairs zero components. `__wt_random_init` seeds a new state from a session RNG or from clock and pid when no session exists. `__left_circular_shift64` and `MAKE_SEED` support seed mixing.

## Control Flow
Default initialization writes fixed W/Z constants. Seed initialization creates a mixed 64-bit value from the input and rotated variants, then combines the component fields with default constants. `__wt_random` optionally delegates to `fuzz_get_random` under `ENABLE_ANTITHESIS`; otherwise it copies W and Z locally, replaces zero components with defaults, advances both multiply-with-carry components, stores them back, and returns the combined 32-bit result.

## State and Persistence Behavior
State is the in-memory `WT_RAND_STATE`, either embedded in a session or supplied by a caller. Session RNGs persist for the session lifetime and survive session reset. No persistent random seed is stored on disk.

## Dependencies and Integration Points
The file depends on WiredTiger session state, `__wt_clock`, process id, first-use detection, and optional Antithesis instrumentation. It integrates with skiplist behavior, randomized internal choices, and tests that rely on stable default-seed behavior.

## Risks
The generator is not cryptographically secure. The comments explicitly warn not to change default-seed behavior because existing WiredTiger usage has been validated against it. Concurrent calls may produce duplicate values, which is allowed, but the implementation is careful to avoid corrupting W/Z into unrecoverable zero states by working with local copies. Any new caller that requires strong randomness or cross-thread uniqueness needs a different primitive.

## Test Signals
Tests should include golden sequences for default initialization, seeded sequences for selected seeds, zero-component repair, session first-use initialization, no-session initialization, repeated session reset preserving RNGs, and Antithesis builds returning instrumentation values. Concurrency stress can confirm state does not collapse to permanent zero under races.
