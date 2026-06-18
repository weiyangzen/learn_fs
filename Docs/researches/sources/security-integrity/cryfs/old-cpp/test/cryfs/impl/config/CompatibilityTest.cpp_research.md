# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CompatibilityTest.cpp

Purpose: This file verifies that historical CryFS config blobs, encoded as hex fixtures for older versions and ciphers, can still be decrypted and loaded with the current config code.

Important APIs/types/functions: Includes: gtest/gtest.h, vector, boost/filesystem.hpp, cpp-utils/data/Data.h, vendor_cryptopp/hex.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/tempfile/TempFile.h, cryfs/impl/config/CryConfigFile.h, cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, plus 1 more. Classes/fixtures: CryConfigCompatibilityTest. Helper functions: loadConfigFromHex, storeHexToFile, hexToBinary. Direct tests: CryConfigCompatibilityTest.v0_8_1_with_aes_256_gcm; CryConfigCompatibilityTest.v0_8_1_with_serpent_128_cfb.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It writes binary config data from hex into a temporary file, then loads that file through `CryConfigFile` using a preset password-derived key provider. Persistent state is the temp config file representing legacy on-disk format.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: The test relies on fixed legacy hex fixtures and exact password/cipher compatibility. It is strong for known historical formats but not exhaustive for every old config variant.

Test signals: Primary signals are CryConfigCompatibilityTest.v0_8_1_with_aes_256_gcm; CryConfigCompatibilityTest.v0_8_1_with_serpent_128_cfb. Assertion/mocking density: EXPECT_EQ x4.
