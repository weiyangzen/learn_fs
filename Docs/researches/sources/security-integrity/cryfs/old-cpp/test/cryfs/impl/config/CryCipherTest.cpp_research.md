# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryCipherTest.cpp

Purpose: This file locks down cipher lookup, supported cipher-name enumeration, warning metadata, and encryption-key sizing for CryFS block ciphers.

Important APIs/types/functions: Includes: gtest/gtest.h, gmock/gmock.h, cryfs/impl/config/CryCipher.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h, cpp-utils/data/DataFixture.h, cpp-utils/random/Random.h. Classes/fixtures: CryCipherTest. Helper functions: EXPECT_FINDS_CORRECT_CIPHERS, EXPECT_FINDS_CORRECT_CIPHER, _loadBlock. Direct tests: CryCipherTest.FindsCorrectCipher; CryCipherTest.SupportedCipherNamesContainsACipher; CryCipherTest.ThereIsACipherWithoutWarning; CryCipherTest.ThereIsACipherWithIntegrityWarning; CryCipherTest.EncryptionKeyHasCorrectSize_448; CryCipherTest.EncryptionKeyHasCorrectSize_256; CryCipherTest.EncryptionKeyHasCorrectSize_128.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: No durable state is written; it checks static cipher registry metadata and encrypt/decrypt sizing with in-memory blocks and random keys.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Cipher registry changes can break compatibility or user-facing defaults. Tests focus on registered ciphers and metadata, not full cryptanalytic behavior.

Test signals: Primary signals are CryCipherTest.FindsCorrectCipher; CryCipherTest.SupportedCipherNamesContainsACipher; CryCipherTest.ThereIsACipherWithoutWarning; CryCipherTest.ThereIsACipherWithIntegrityWarning; CryCipherTest.EncryptionKeyHasCorrectSize_448; CryCipherTest.EncryptionKeyHasCorrectSize_256; CryCipherTest.EncryptionKeyHasCorrectSize_128. Assertion/mocking density: EXPECT_EQ x5, EXPECT_NE x1.
