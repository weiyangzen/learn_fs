# sources/storage-engines/wiredtiger/test/csuite/random/main.c

Purpose: deterministic regression test for WiredTiger's default random number generator sequence. It verifies that values at powers-of-two call counts match a fixed expected array.

Important APIs, types, and functions: `EXPECTED_RANDOM` stores 35 expected `uint32_t` values. `test_random` initializes `WT_RAND_STATE` with `__wt_random_init_default`, repeatedly calls `__wt_random`, and checks the generated value whenever the call count equals `1 << i`. `usage` and `main` handle the optional `-v` flag.

Control flow: `main` sets the program name, skips under `ENABLE_ANTITHESIS`, parses `-v`, rejects extra arguments, and calls `test_random`. In verbose mode, the test prints the index, count, and random value at each checked power of two.

State and persistence behavior: no database is opened and no files are written. The only state is the local RNG state and loop counters.

Dependencies and integration points: depends on WiredTiger internal random APIs exposed through `test_util.h`. This test is a compatibility guard for deterministic PRNG behavior used by other tests and reproducibility.

Risks: intentional changes to the RNG algorithm or default seed sequence require updating `EXPECTED_RANDOM` and may affect reproducibility of many seeded tests. The loop count grows to the last power-of-two checkpoint, so adding many more expected values can increase runtime sharply.

Test signals: zero exit means every checked power-of-two output matched. Verbose output is useful when regenerating the expected sequence after an intentional algorithm change.
