# sources/storage-engines/foundationdb/fdbserver/core/WorkloadKeys.cpp

## sources/storage-engines/foundationdb/fdbserver/core/WorkloadKeys.cpp

Purpose: encodes doubles into deterministic test keys and decodes them back for workload/test key generation.

Important APIs: `doubleToTestKey(double)`, `testKeyToDouble(const KeyRef&)`, and prefix overloads for both directions.

Control flow and state: encoding treats the double bits as a `uint64_t` and formats them as a 16-character hexadecimal string. Decoding scans the hex string into a `uint64_t` and reinterprets the bits as a double. Prefix overloads add or remove a supplied key prefix.

Dependencies and integration: depends on C stdio/inttypes formatting, `WorkloadKeys.h`, and Flow key types. It is intended for workloads that need reproducible numeric keys.

Risks and tests: the implementation uses type punning through casts, so portability depends on platform representation and aliasing assumptions already common in this codebase. Lexicographic order is bit-pattern order, not necessarily numeric order for all doubles. Tests should cover round trips, prefix handling, NaN/negative/zero values, and fixed expected encodings.
