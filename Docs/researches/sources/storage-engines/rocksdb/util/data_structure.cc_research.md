# sources/storage-engines/rocksdb/util/data_structure.cc

Purpose: out-of-line helpers for RocksDB public/internal data-structure support, specifically small enum-set bit operations.

Important APIs: `detail::CountTrailingZeroBitsForSmallEnumSet(uint64_t)` delegates to `CountTrailingZeroBits()`. `detail::BitsSetToOneForSmallEnumSet(uint64_t)` delegates to `BitsSetToOne()`.

Control flow: both functions are single-call wrappers around `util/math.h` functions.

State and persistence: no state or persistence. Behavior depends only on input bit patterns.

Dependencies and integration: includes `rocksdb/data_structure.h` and `util/math.h`. These wrappers keep some implementation details out of headers while exposing stable functions for small enum set internals.

Risks: minimal. Semantics must remain aligned with the public `data_structure.h` expectations, especially for zero inputs if callers depend on math helper behavior.

Test signals: no direct test in this subset; coverage is likely through users of small enum sets.
