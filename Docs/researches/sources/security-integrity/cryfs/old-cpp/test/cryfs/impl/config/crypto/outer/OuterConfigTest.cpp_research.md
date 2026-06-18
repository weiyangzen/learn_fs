# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterConfigTest.cpp

Purpose: This file tests serialization of outer config metadata, including encrypted inner data and KDF/key-configuration data.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/data/DataFixture.h, cryfs/impl/config/crypto/outer/OuterConfig.h, boost/optional/optional_io.hpp. Classes/fixtures: OuterConfigTest. Helper functions: kdfParameters. Direct tests: OuterConfigTest.SomeValues; OuterConfigTest.DataEmpty; OuterConfigTest.KeyConfigEmpty; OuterConfigTest.DataAndKeyConfigEmpty; OuterConfigTest.InvalidSerialization.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is serialized/deserialized `OuterConfig` values with optional empty data/key-config combinations.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Outer config parsing is the first compatibility gate for encrypted config files.

Test signals: Primary signals are OuterConfigTest.SomeValues; OuterConfigTest.DataEmpty; OuterConfigTest.KeyConfigEmpty; OuterConfigTest.DataAndKeyConfigEmpty; OuterConfigTest.InvalidSerialization. Assertion/mocking density: EXPECT_EQ x9.
