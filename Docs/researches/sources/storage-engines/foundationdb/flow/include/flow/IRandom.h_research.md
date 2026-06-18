# sources/storage-engines/foundationdb/flow/include/flow/IRandom.h

## Purpose
`IRandom.h` defines Flow's random generator interface, UID value type, comparison helpers, and accessors for deterministic, nondeterministic, and debug random streams.

## Important APIs, Types, And Functions
Important items are overloaded `compare()`, `UID`, `scalar_traits<UID>`, `Traceable<UID>`, `std::hash<UID>`, `IRandom`, `setThreadLocalDeterministicRandomSeed()`, `deterministicRandom()`, `nondeterministicRandom()`, `debugRandom()`, and Swift helper `swift_get_randomInt64()`.

## Control Flow
`IRandom` implementers provide primitive random methods; default helpers choose/shuffle containers, coin flip, and exponential-bucket random values. `UID` converts to/from strings and serializes as two unversioned 64-bit words.

## State And Persistence Behavior
`UID` persists two 64-bit parts and is used in serialized data; its format is explicitly unversioned. Random generator state lives in implementations. Deterministic random may be seeded per thread.

## Dependencies And Integration Points
It depends on platform support, file identifiers, serializer traits, `FastRef`, `Traceable`, and hash containers. It is used broadly for simulation, network address selection, IDs, buggify, encryption test randomization, and load balancing.

## Risks And Edge Cases
`debugRandom()` is warned as not thread safe and must not perturb simulator determinism. `randomExp()` uses shifts and expects sensible exponents. `truePercent()` disallows 0 and 100 by contract. UID serialization changes would affect key definitions.

## Test Signals
UID string/serialization/hash tests, deterministic seed reproducibility, shuffle/choice bounds, exponential bucket coverage, true-percent validation, thread-local seed isolation, and simulator replay determinism are important.
