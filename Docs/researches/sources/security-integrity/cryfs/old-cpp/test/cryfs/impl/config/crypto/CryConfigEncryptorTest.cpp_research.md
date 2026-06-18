# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorTest.cpp

Purpose: This file tests the full config encryptor that combines outer key-configuration encryption with inner payload encryption and selected cipher metadata.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/data/DataFixture.h, cpp-utils/crypto/symmetric/ciphers.h, cryfs/impl/config/crypto/CryConfigEncryptor.h, boost/optional/optional_io.hpp. Classes/fixtures: CryConfigEncryptorTest. Helper functions: makeEncryptor, changeInnerCipherFieldTo, _derivedKey, _kdfParameters, _outerEncryptor, _decryptInnerConfig, _encryptInnerConfig. Direct tests: CryConfigEncryptorTest.EncryptAndDecrypt_Data_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Data_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_EmptyData; CryConfigEncryptorTest.InvalidCiphertext; CryConfigEncryptorTest.DoesntEncryptWhenTooLarge; CryConfigEncryptorTest.EncryptionIsFixedSize; CryConfigEncryptorTest.SpecifiedInnerCipherIsUsed.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is serialized encrypted data, KDF parameters, derived keys, and optional inner config fields in memory.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Size limits, fixed-size ciphertext expectations, and inner-cipher selection are compatibility-critical for persisted config files.

Test signals: Primary signals are CryConfigEncryptorTest.EncryptAndDecrypt_Data_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Data_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_AES; CryConfigEncryptorTest.EncryptAndDecrypt_Cipher_Twofish; CryConfigEncryptorTest.EncryptAndDecrypt_EmptyData; CryConfigEncryptorTest.InvalidCiphertext; CryConfigEncryptorTest.DoesntEncryptWhenTooLarge; CryConfigEncryptorTest.EncryptionIsFixedSize. Assertion/mocking density: EXPECT_EQ x9, EXPECT_THROW x1.
