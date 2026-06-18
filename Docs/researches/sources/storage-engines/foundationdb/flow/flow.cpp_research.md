# sources/storage-engines/foundationdb/flow/flow.cpp

Purpose: provides core Flow runtime globals, deterministic randomness helpers, UID/string utilities, formatting helpers, OpenSSL deterministic RNG binding, memcpy override glue, and unit tests for serialization and utility functions.

Important APIs/types/functions: globals `g_network`, `startSampling`, lineage references, RNG references, `randLog`, `noUnseed`; functions `setThreadLocalDeterministicRandomSeed`, `debugRandom`, `deterministicRandom`, `nondeterministicRandom`, `UID::toString/fromString/fromStringThrowsOnFailure/shortString`, `parse_with_suffix`, `parseDuration`, `vsformat`, `format`, `strinc`, `addVersionStampAtEnd`, `bindDeterministicRandomToOpenssl`, `nChooseK`, and `rte_memcpy_noinline`.

Control flow: RNG access lazily initializes thread-local deterministic generators from platform seeds. UID parsing validates fixed 32-character hex strings. Suffix parsing converts storage/duration units. OpenSSL binding installs a `RAND_METHOD` that draws from Flow deterministic random and asserts simulation when `g_network` exists.

State/persistence: owns process/thread globals for network, RNG, lineage, and debug tokens. No durable on-disk persistence.

Dependencies/integration: OpenSSL/BoringSSL, fmt, Flow platform, errors, deterministic random, unit tests, serialization. The optional AVX/Linux memcpy override exports a default `memcpy` symbol using `rte_memcpy`.

Risks: global state is central and ordering-sensitive. Overriding `memcpy` is platform/compiler/sanitizer gated and high blast radius. `strinc` asserts non-all-0xff input. OpenSSL deterministic binding should only be used in simulation.

Test signals: unit tests cover `ErrorOr`, `Optional`, `Standalone`, noSim presence, `ErrorOr::map/flatMap`, and human-readable byte/duration formatting.
