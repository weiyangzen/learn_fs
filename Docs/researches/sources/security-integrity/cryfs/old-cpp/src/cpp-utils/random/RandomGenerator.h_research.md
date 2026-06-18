# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGenerator.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 46 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `RandomGenerator`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_RANDOMGENERATOR_H`. Important declarations or call sites include `RandomGenerator();`; `template<size_t SIZE> FixedSizeData<SIZE> getFixedSize();`; `Data get(size_t size);`; `void write(void *target, size_t size);`; `virtual void _get(void *target, size_t bytes) = 0;`; `DISALLOW_COPY_AND_ASSIGN(RandomGenerator);`; `inline RandomGenerator::RandomGenerator() {`; `inline void RandomGenerator::write(void *target, size_t size) {`; `_get(target, size);`; `template<size_t SIZE> inline FixedSizeData<SIZE> RandomGenerator::getFixedSize() {`. CMake commands used here include `RandomGenerator`, `DISALLOW_COPY_AND_ASSIGN`, `_get`. Primary includes/dependencies visible in the file include `../data/FixedSizeData.h`, `../data/Data.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../data/FixedSizeData.h`, `../data/Data.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.
