# sources/test-tools/stress-ng/stress-hash.c

## Purpose
`stress-hash.c` benchmarks and validates many string hash implementations from stress-ng's `core-hash` helpers and optional xxHash. It measures hash throughput and a simple bucket-distribution chi-squared score.

## Important APIs, Types, And Functions
`stress_hash_stats_t` tracks duration, chi-squared score, and total hashes. `stress_bucket_t` contains 256 buckets and a 128-byte key buffer. `stress_hash_method_info_t` maps method names to callbacks. `stress_hash_generic()` generates an ASCII random buffer, hashes every suffix length from 127 down to 1, updates bucket counts, computes the distribution score, and optionally verifies a checksum. Method wrappers adapt functions such as adler32, Jenkin, Murmur3, PJW, djb2a, fnv1a, sdbm, crc32c, xor, mul/add, coffin, x17, loselose, Knuth, mid5, xorror, and optional `XXH64`.

## Control Flow
`stress_hash()` reads `hash-method`, zeroes global per-method stats, waits at the barrier, then repeatedly calls the selected method. Method `all` rotates through all concrete methods using a static index. On exit, instance zero prints per-method rates and chi-squared values for methods that ran.

## State And Persistence
State is process-local and in memory: static stats for each method, the static rotating index in `stress_hash_all()`, the stack bucket, and stress-ng random state. There is no external persistence.

## Dependencies And Integration Points
It depends on `core-hash.h`, endian detection, random buffer helpers, metrics/logging, and optional `xxhash.h` plus `libxxhash`. Verification is controlled by global stress-ng verify flags.

## Risks
Checksum constants are endian-sensitive for some methods and can break with algorithm changes, compiler issues, or different helper semantics. The `all` method's static index is not reset per invocation within a process. Chi-squared is a rough distribution signal, not a statistical test of full hash quality.

## Test Signals
Run every advertised `hash-method`, verify checksum pass on little- and big-endian targets, optional xxHash inclusion/exclusion, sane printed rates, and no failures under repeated `all` rotation.
