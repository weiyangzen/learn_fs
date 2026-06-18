# sources/storage-engines/rocksdb/util/ribbon_impl.h

## Purpose
Provides standard concrete Ribbon hasher, banding storage, and solution storage implementations parameterized by a `TypesAndSettings` concept.

## Important APIs, Types, And Functions
`AddInputSelector` chooses key-only inputs for filters or key/result pairs for PHSFs. `StandardHasher` implements hashing, start selection, coefficient-row generation, result-row derivation, raw/ordinal seed translation, and seed premixing. `StandardRehasherAdapter`/`StandardRehasher` support building filters from existing hashes. `ExpectedCollisionFpRate` estimates hash-collision false positives. `StandardBanding` owns coefficient/result rows, supports `Reset`, `AddRange`, `AddRangeOrRollBack`, `Add`, `GetOccupiedCount`, `ResetAndFindSeedToSolve`, and memory estimation. `InMemSimpleSolution` and `SerializableInterleavedSolution` implement simple row-major and serializable interleaved solution storage.

## Control Flow
`StandardHasher::GetStart` maps hashes to starts using `FastRangeGeneric`, optionally "smashing" some range into front/back slots for better edge utilization. `GetCoeffRow` expands 32- or 64-bit hashes into coefficient rows, using alternate 128-bit multiplication for smash mode and ensuring non-zero or first-bit-one rows. `StandardBanding::ResetAndFindSeedToSolve` loops ordinal seeds, resets storage, and calls `AddRange` until construction succeeds or the seed mask wraps. Solution storage calls generic back-substitution and then answers PHSF/filter queries through simple or interleaved query algorithms.

## State And Persistence
`StandardHasher` stores only `raw_seed_`. `StandardBanding` owns mutable construction arrays and backtrack storage; this is temporary build state. `InMemSimpleSolution` owns in-memory solution rows. `SerializableInterleavedSolution` does not own its external byte buffer, but encodes/decodes little-endian `CoeffRow` segments into it and adjusts effective `data_len_` to the number of usable segments; this buffer is the persistence-ready filter/PHSF payload.

## Dependencies And Integration Points
Depends on `ribbon_alg.h`, `port/port.h` for prefetch/cache constants, and `util/fastrange.h`. It integrates with Ribbon configuration helpers, RocksDB filter construction, and tests. The `IMPORT_RIBBON_IMPL_TYPES` macro gives convenient aliases for template-heavy callers.

## Risks
`TypesAndSettings` must provide compatible unsigned types and a high-quality seeded hash. Seed premixing compensates for some weak sequential-seed behavior but is not a full hash. `SerializableInterleavedSolution` borrows a buffer and assumes it remains valid and suitably sized/aligned for byte access. Zero-start and zero-byte cases intentionally return always false or always true depending on configuration and can surprise callers. Fractional-column FP calculations approximate smash effects. Rehasher mode is not recommended for general PHSFs because original hash collisions can block construction.

## Test Signals
`ribbon_test.cc` exercises a large matrix of settings: coefficient widths, smash, homogeneous mode, result widths, index sizes, 32-bit hashes, string keys, seed widths, no-first-bit mode, zero starts, rehasher variants, and small-key generators. Tests compare simple and interleaved solutions, expected FP rates, raw/ordinal seed reversibility, and PHSF value recovery.
