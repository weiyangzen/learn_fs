# sources/test-tools/fio/lib/rand.c

Purpose: fio pseudo-random generator initialization and buffer-filling utilities.

Important APIs/functions: `init_rand`, `init_rand_seed`, `__init_rand64`, `__fill_random_buf`, `fill_random_buf`, `__fill_random_buf_percentage`, and `fill_random_buf_percentage`. It supports 32-bit Taus88 and 64-bit Taus258 state from inline generators in `rand.h`.

Control flow: seeding uses LCG steps with minimum state constraints and cranks the generator several times. Buffer filling obtains a seed, hashes it through one or multiple seed buckets, and writes deterministic 64-bit words plus tail bytes. Percentage filling alternates random chunks with zero or caller pattern chunks per segment.

State/persistence: mutates caller-owned `frand_state`; writes caller buffers. Global `arch_random` is declared but not used in this file.

Dependencies/integration: depends on `pattern.h` for `cpy_pattern` and `hash.h` for `__hash_u64`. Used throughout fio for repeatable data patterns and random decisions.

Risks/test signals: expressions like `(2^31)` are C XOR, not exponentiation, but may be inherited intentionally from old seeding code; changing them affects reproducibility. Percentage math and segment tails need boundary tests. Signals include deterministic seeds, identical buffers for identical seeds, and correct pattern/random ratios.
