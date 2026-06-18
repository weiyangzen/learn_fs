# sources/storage-engines/foundationdb/flow/DeterministicRandom.cpp

## Purpose
`DeterministicRandom.cpp` implements the deterministic random generator used throughout Flow tests and simulation, with reproducible integer, floating, byte, id, string, and probability helpers.

## Important APIs, Types, and Functions
Core methods include `gen64`, constructor, `random01`, `randomInt`, `randomInt64`, `randomUInt32`, `randomUInt64`, `randomSkewedUInt32`, `randomUniqueID`, `randomAlphaNumeric`, `randomBytes`, `truePercent`, `peek`, `resetSeed`, `addref`, and `delref`.

## Control Flow
The generator keeps one prefetched `next` value. `gen64` returns it, advances the underlying RNG, and optionally emits a sampled trace. Range methods modulo the 64-bit output into requested ranges while handling negative minima. Byte generation writes chunks of generated 64-bit values. Optional `randLog` output records generated values when enabled.

## State and Persistence Behavior
State is in-memory RNG state: the underlying engine, prefetched `next`, and whether random logging is enabled. `resetSeed` restores reproducible sequence state for a seed. There is no durable persistence unless `randLog` points to an external log file.

## Dependencies and Integration Points
The file depends on fmt, `Arena`, `DeterministicRandom.h`, `UnitTest`, Flow tracing, `UID`, `StringRef`, and reference counting. It is used heavily across workloads and unit tests to keep randomized behavior deterministic under simulation seeds.

## Risks and Edge Cases
Modulo reduction is simple and can introduce bias, acceptable for simulation/test randomness but not cryptographic use. `truePercent` asserts the percent is strictly between 0 and 100, so callers needing 0 or 100 must special-case. Negative range arithmetic is carefully unsigned and worth preserving.

## Test Signals
The `/flow/DeterministicRandom/truePercent` test checks 1, 50, and 99 percent ranges under fixed seeds, same-seed determinism, and ordering across probabilities.
