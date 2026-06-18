# sources/storage-engines/rocksdb/util/ribbon_alg.h

## Purpose
Defines the generic core algorithms for Ribbon PHSFs and Ribbon filters: incremental banding over GF(2), optional backtracking, back-substitution, and query routines for simple and interleaved solution layouts.

## Important APIs, Types, And Functions
Concept-style contracts document required hasher, banding storage, backtrack storage, and solution storage APIs. `BandingAdd` inserts one equation into an upper-triangular band matrix. `BandingAddRange` processes input ranges with optional prefetch and rollback. `SimpleBackSubst`, `SimpleQueryHelper`, `SimplePhsfQuery`, and `SimpleFilterQuery` support row-major solutions. `BackSubstBlock`, `InterleavedBackSubst`, `InterleavedPrepareQuery`, `InterleavedPhsfQuery`, and `InterleavedFilterQuery` support the serialized interleaved layout.

## Control Flow
Banding hashes each input to a start, coefficient row, and result row, then performs on-the-fly Gaussian elimination by XORing with an occupied row at the same leading column until an empty row is found or the equation reduces to zero. On failure, optional backtracking clears rows written during the batch. Back-substitution walks slots backward, maintaining column-major state for the last `kCoeffBits` solution rows. Query paths hash the key, compute start and coefficients, load one or two solution blocks, parity the selected bits, and compare with expected result bits for filters.

## State And Persistence
The algorithms themselves are stateless templates; state lives in caller-provided storage. Banding storage represents an intermediate upper-triangular system. Solution storage represents the final PHSF/filter data and may be persisted by concrete implementations. Backtracking storage is transient and clears rows on failed speculative adds.

## Dependencies And Integration Points
Depends on `util/math128.h` and math/bit primitives such as `CountTrailingZeroBits` and `BitParity`. It is consumed by `ribbon_impl.h`, which supplies standard storage and hasher implementations, and by Ribbon tests. Integration is template-based, so compile-time type compatibility and unsigned integer sizes are enforced through `static_assert`.

## Risks
The algorithms assume coefficient rows are non-zero and storage contracts are honored. If `kFirstCoeffAlwaysOne` is incorrectly declared, banding can misplace equations. Backtracking only works if the backtrack storage can record every row written in the batch. Interleaved query logic is sensitive to block boundaries, start-bit shifts, segment counts, and fractional-column configuration. Homogeneous filters intentionally fill unconstrained rows differently in concrete storage, affecting false positive behavior.

## Test Signals
`ribbon_test.cc` stress-tests these algorithms through many `TypesAndSettings`: construction success/reseed rates, backtracking rollback, false-positive distribution, simple vs interleaved equivalence, PHSF mapping correctness, zero-start behavior, and occupancy exploration tooling.
