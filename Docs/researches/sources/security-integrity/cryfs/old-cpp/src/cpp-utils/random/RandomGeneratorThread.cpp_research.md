# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/RandomGeneratorThread.cpp

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 34 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Important declarations or call sites include `_thread(std::bind(&RandomGeneratorThread::_loopIteration, this), "RandomGeneratorThread") {`; `ASSERT(_maxSize >= _minSize, "Invalid parameters");`; `void RandomGeneratorThread::start() {`; `return _thread.start();`; `bool RandomGeneratorThread::_loopIteration() {`; `_buffer->waitUntilSizeIsLessThan(_minSize);`; `size_t neededRandomDataSize = _maxSize - _buffer->size();`; `ASSERT(_maxSize > _buffer->size(), "This could theoretically fail if another thread refilled the buffer. But we should be the o...`; `Data randomData = _generateRandomData(neededRandomDataSize);`; `_buffer->add(randomData);`. CMake commands used here include `_buffer`, `_minSize`, `_maxSize`, `_thread`, `ASSERT`. Primary includes/dependencies visible in the file include `RandomGeneratorThread.h`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `RandomGeneratorThread.h`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.
