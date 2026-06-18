# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/InnerConfigTest.cpp

Purpose: This file tests serialization of inner config metadata, especially encrypted data and cipher-name fields.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/data/DataFixture.h, cryfs/impl/config/crypto/inner/InnerConfig.h, boost/optional/optional_io.hpp. Classes/fixtures: none visible. Helper functions: none visible. Direct tests: InnerConfigTest.SomeValues; InnerConfigTest.DataEmpty; InnerConfigTest.CipherNameEmpty; InnerConfigTest.DataAndCipherNameEmpty; InnerConfigTest.InvalidSerialization.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is in-memory serialized/deserialized `InnerConfig` values, including empty-field cases and invalid serialization input.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Field absence/emptiness semantics must remain stable for config compatibility.

Test signals: Primary signals are InnerConfigTest.SomeValues; InnerConfigTest.DataEmpty; InnerConfigTest.CipherNameEmpty; InnerConfigTest.DataAndCipherNameEmpty; InnerConfigTest.InvalidSerialization. Assertion/mocking density: EXPECT_EQ x9.
