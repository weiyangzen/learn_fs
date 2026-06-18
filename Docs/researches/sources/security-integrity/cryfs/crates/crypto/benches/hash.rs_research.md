# sources/security-integrity/cryfs/crates/crypto/benches/hash.rs

## Purpose
Criterion benchmark comparing SHA-512 hashing throughput across the default, pure Rust, OpenSSL, and libsodium backends over several input sizes.

## Important APIs, types, and functions
- `data(size, seed)` produces deterministic random `Data`.
- `bench_hash` benchmarks `Sha512`, `Sha2Sha512`, `OpensslSha512`, and `LibsodiumSha512`.
- Uses `Salt::generate_random`, `HashAlgorithm::hash`, `BenchmarkId`, and `black_box`.

## Control flow
For each size from one byte to one MiB, the benchmark creates a salt and deterministic data per backend registration, then repeatedly hashes in Criterion iterations.

## State and persistence behavior
No persistent state. Inputs are deterministic except salts are generated once per benchmark case, outside the measured loop.

## Dependencies and integration points
Integrates the public `cryfs_crypto::hash` API with Criterion and `cryfs_utils::Data`, providing comparative backend performance signals.

## Risks and edge cases
Salt generation is excluded from timing, which is appropriate for hashing backend throughput but not full operation cost. The one-MiB maximum avoids very long benches; larger commented sizes are not measured by default.

## Test signals
Criterion reports per-backend latency/throughput by input size; it is a performance signal, not a correctness test.
