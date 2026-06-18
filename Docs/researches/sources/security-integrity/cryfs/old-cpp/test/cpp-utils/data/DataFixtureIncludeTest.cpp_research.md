# sources/security-integrity/cryfs/old-cpp/test/cpp-utils/data/DataFixtureIncludeTest.cpp

Purpose: Compile-only public include test for `cpp-utils/data/DataFixture.h`.

Important APIs and types: Includes `DataFixture.h` without using other test utilities in this file.

Control flow: No runtime tests are defined; the build verifies that the header is self-contained enough for direct inclusion.

State and persistence behavior: No runtime state or persistence.

Dependencies and integration points: Protects downstream tests and users that include the fixture header directly for deterministic data generation.

Risks: Compile-only coverage cannot detect incorrect generated data, only include and dependency regressions.

Test signals: Successful compilation of the `cpp-utils-test` target with this source present.
