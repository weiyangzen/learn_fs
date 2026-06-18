# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataIncludeTest.cpp

Purpose: Compile-only include test for the public `cpp-utils/data/Data.h` header.

Important APIs and types: Includes `Data.h` directly and defines no tests.

Control flow: Build system compiles the translation unit to verify the header's standalone include contract.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Protects the main byte-buffer abstraction used across crypto, blockstore, serialization, and test fixtures.

Risks: Compile-only tests do not validate `Data` behavior; semantic coverage is in `DataTest.cpp`.

Test signals: Successful compilation without hidden include-order requirements.
