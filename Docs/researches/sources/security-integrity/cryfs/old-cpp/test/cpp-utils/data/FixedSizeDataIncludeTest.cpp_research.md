# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/FixedSizeDataIncludeTest.cpp

Purpose: Compile-only include test for `cpp-utils/data/FixedSizeData.h`.

Important APIs and types: Includes `FixedSizeData.h` directly.

Control flow: No runtime logic; the compiler validates header independence.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Protects callers that use fixed-length byte arrays for hashes, IDs, keys, and serialized values.

Risks: Does not validate data semantics; `FixedSizeDataTest.cpp` carries behavioral coverage.

Test signals: Successful compilation without missing transitive includes.
