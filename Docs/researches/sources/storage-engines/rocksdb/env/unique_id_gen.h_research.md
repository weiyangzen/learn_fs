# sources/storage-engines/rocksdb/env/unique_id_gen.h

## Purpose
`unique_id_gen.h` declares internal APIs for extracting environment entropy and generating unique identifiers. It distinguishes these utilities from algorithmic pseudorandomness in `random.h` and notes possible future migration to public `Env` APIs.

## Important APIs and types
`GenerateRawUniqueId(uint64_t* a, uint64_t* b, bool exclude_port_uuid=false)` returns a probabilistically globally unique 128-bit value split across two 64-bit words. Debug builds declare `TEST_GenerateRawUniqueId()` with switches for excluding UUID, environment details, and random-device sources.

`SemiStructuredUniqueIdGen` stores `base_upper_`, `base_lower_`, an atomic counter, and a saved process ID. It provides `Reset()`, `GenerateNext(uint64_t*, uint64_t*)`, a templated integral `GenerateNext<T>()`, and `GetBaseUpper()`. It is optimized for many IDs per generator by combining a random base with a guaranteed local counter sequence.

`UnpredictableUniqueIdGen` is cache-line aligned, owns a four-word atomic entropy pool plus counter, and exposes `Reset()`, `GenerateNext()`, and `GenerateNextWithEntropy()`. Debug builds include a zero-initialized constructor and counter accessor.

## State, dependencies, and integration
The header depends on port cache-line alignment, atomics, type traits, and the RocksDB namespace header. It documents expected integration with DB session IDs and DB identity generation fallbacks.

## Risks and test signals
The contract is probabilistic and explicitly non-cryptographic. `Reset()` on both generators is not thread safe, while generation is intended to be thread safe. Smaller templated outputs intentionally cycle through all low-word possibilities only within the semi-structured generator's counter assumptions. Tests should verify API compile behavior, process/fork fallback, no duplicate IDs under multithreaded generation, debug challenge modes, and correct alignment/atomic sanitizer behavior.
