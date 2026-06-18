# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/outer/OuterEncryptorTest.cpp

Purpose: This file tests the outer encryptor that wraps inner config data with password-derived key information and enforces invalid-data/size/fixed-size behavior.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/crypto/outer/OuterEncryptor.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, boost/optional/optional_io.hpp. Classes/fixtures: OuterEncryptorTest. Helper functions: kdfParameters, makeOuterEncryptor. Direct tests: OuterEncryptorTest.EncryptAndDecrypt; OuterEncryptorTest.EncryptAndDecrypt_EmptyData; OuterEncryptorTest.InvalidCiphertext; OuterEncryptorTest.DoesntEncryptWhenTooLarge; OuterEncryptorTest.EncryptionIsFixedSize.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: All state is in-memory plaintext, ciphertext, KDF parameters, and derived keys.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Outer encryption failure prevents all config loading, while lax invalid-ciphertext handling could accept corrupt config files.

Test signals: Primary signals are OuterEncryptorTest.EncryptAndDecrypt; OuterEncryptorTest.EncryptAndDecrypt_EmptyData; OuterEncryptorTest.InvalidCiphertext; OuterEncryptorTest.DoesntEncryptWhenTooLarge; OuterEncryptorTest.EncryptionIsFixedSize. Assertion/mocking density: EXPECT_EQ x5, EXPECT_THROW x1.
