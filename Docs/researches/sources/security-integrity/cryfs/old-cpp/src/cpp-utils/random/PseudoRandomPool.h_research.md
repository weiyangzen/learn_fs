# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/PseudoRandomPool.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 40 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `PseudoRandomPool`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_PSEUDORANDOMPOOL_H`. Important declarations or call sites include `PseudoRandomPool();`; `void _get(void *target, size_t bytes) override;`; `DISALLOW_COPY_AND_ASSIGN(PseudoRandomPool);`; `inline void PseudoRandomPool::_get(void *target, size_t bytes) {`; `_buffer.get(target, bytes);`; `inline PseudoRandomPool::PseudoRandomPool(): _buffer(), _refillThread(&_buffer, MIN_BUFFER_SIZE, MAX_BUFFER_SIZE) {`; `_refillThread.start();`. CMake commands used here include `PseudoRandomPool`, `DISALLOW_COPY_AND_ASSIGN`. Primary includes/dependencies visible in the file include `boost/thread.hpp`, `RandomGenerator.h`, `ThreadsafeRandomDataBuffer.h`, `RandomGeneratorThread.h`, `mutex`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `boost/thread.hpp`, `RandomGenerator.h`, `ThreadsafeRandomDataBuffer.h`, `RandomGeneratorThread.h`, `mutex`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.
