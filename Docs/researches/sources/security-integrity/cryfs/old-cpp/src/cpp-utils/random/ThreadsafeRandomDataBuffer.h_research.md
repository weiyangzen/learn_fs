# sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random/ThreadsafeRandomDataBuffer.h

## Purpose
Implements random byte generation, buffered pseudorandom supply, OS randomness, and background refill support for crypto and ID generation. This specific file has 81 source lines under `sources/security-integrity/cryfs/old-cpp/src/cpp-utils/random` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ThreadsafeRandomDataBuffer`. Macros/constants: `MESSMER_CPPUTILS_RANDOM_THREADSAFERANDOMDATABUFFER_H`. Important declarations or call sites include `ThreadsafeRandomDataBuffer();`; `size_t size() const;`; `void get(void *target, size_t numBytes);`; `void add(const Data& data);`; `void waitUntilSizeIsLessThan(size_t numBytes);`; `size_t _get(void *target, size_t bytes);`; `DISALLOW_COPY_AND_ASSIGN(ThreadsafeRandomDataBuffer);`; `inline ThreadsafeRandomDataBuffer::ThreadsafeRandomDataBuffer(): _buffer(), _mutex(), _dataAddedCv(), _dataGottenCv() {`; `inline size_t ThreadsafeRandomDataBuffer::size() const {`; `boost::unique_lock<boost::mutex> lock(_mutex);`. CMake commands used here include `ThreadsafeRandomDataBuffer`, `DISALLOW_COPY_AND_ASSIGN`, `while`, `ASSERT`. Primary includes/dependencies visible in the file include `../data/Data.h`, `../assert/assert.h`, `RandomDataBuffer.h`, `boost/thread.hpp`.

## Control Flow
Random generation writes into caller buffers through a virtual `_get`; the pseudorandom pool drains a threadsafe buffer while a loop thread refills it from Crypto++ random data between configured thresholds.

## State and Persistence Behavior
The pseudorandom pool stores buffered random `Data` and a background refill thread. OS random generators are process objects; random bytes are not persisted unless callers store them.

## Dependencies and Integration Points
Integrates with Crypto++, cpp-utils `Data`/`FixedSizeData`, random generators, and CryFS key/cipher selection code; visible includes are `../data/Data.h`, `../assert/assert.h`, `RandomDataBuffer.h`, `boost/thread.hpp`.

## Risks and Edge Cases
The pseudorandom pool is used for IVs and IDs, so refill thread lifecycle and buffer synchronization matter. Security-sensitive key generation should use OS randomness where intended.

## Test Signals
Test requested byte counts, buffer refill thresholds, threadsafe draining, OS random availability, and deterministic absence of repeated fixed buffers under load.
