# sources/storage-engines/wiredtiger/test/csuite/random_session/main.c

Purpose: verifies that WiredTiger random number generation is sufficiently distinct across seeds and across sessions, especially when sessions are opened close together in time.

Important APIs, types, and functions: constants `N_SESSIONS` and `N_SEQUENTIAL_DIFFS` bound comparisons. `test_rng_seq` compares two seeded RNG streams. `test_rng_init` compares the first number from many different seeds. `main` opens WiredTiger, casts sessions to `WT_SESSION_IMPL`, and reads each session's `rnd_random` state with `__wt_random`.

Control flow: `main` parses standard test options, runs seed-sequence checks, creates `WT_TEST.random_session`, opens a small WiredTiger connection, then performs a single-session test by opening/closing one session at a time and checking adjacent first numbers differ in more than half the cases. It then opens ten sessions rapidly, runs 100 cycles, generates one number per session per cycle, and checks that each session's number differs from the first and from peers in more than half the comparisons. It closes sessions, closes the connection, removes the home unless preserved, and asserts `random_numbers_repeated` remains false.

State and persistence behavior: creates a temporary WiredTiger home but no tables. Important mutable state is per-session internal RNG state. The short sleeps reset timeslices to increase the chance sessions are opened close together, which is the collision scenario under test.

Dependencies and integration points: depends on internal `WT_SESSION_IMPL::rnd_random`, random initialization functions, public connection/session APIs, and `testutil_parse_opts`. It complements `random/main.c`, which checks the exact default sequence.

Risks: statistical assertions are simple thresholds, not formal randomness tests. Accessing `WT_SESSION_IMPL` ties the test to internal structure layout. The variable `random_numbers_repeated` is never set, so the final assertion is currently redundant.

Test signals: zero exit means seeded RNG streams and rapidly opened session RNGs differ often enough by full value and modulo 2048. Verbose mode prints the generated values.
