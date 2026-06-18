# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/inner/ConcreteInnerEncryptorTest.cpp

Purpose: This file tests a concrete inner encryptor for config payload data across AES/Twofish paths, empty data, wrong cipher names, invalid ciphertext, size limits, and fixed encrypted size.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/crypto/inner/ConcreteInnerEncryptor.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, boost/optional/optional_io.hpp. Classes/fixtures: ConcreteInnerEncryptorTest. Helper functions: makeInnerEncryptor. Direct tests: ConcreteInnerEncryptorTest.EncryptAndDecrypt_AES; ConcreteInnerEncryptorTest.EncryptAndDecrypt_Twofish; ConcreteInnerEncryptorTest.EncryptAndDecrypt_EmptyData; ConcreteInnerEncryptorTest.DoesntDecryptWithWrongCipherName; ConcreteInnerEncryptorTest.InvalidCiphertext; ConcreteInnerEncryptorTest.DoesntEncryptWhenTooLarge; ConcreteInnerEncryptorTest.EncryptionIsFixedSize.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: All state is in-memory plaintext, ciphertext, cipher names, and keys.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Inner encryptor regressions can invalidate config payloads even when outer key wrapping succeeds.

Test signals: Primary signals are ConcreteInnerEncryptorTest.EncryptAndDecrypt_AES; ConcreteInnerEncryptorTest.EncryptAndDecrypt_Twofish; ConcreteInnerEncryptorTest.EncryptAndDecrypt_EmptyData; ConcreteInnerEncryptorTest.DoesntDecryptWithWrongCipherName; ConcreteInnerEncryptorTest.InvalidCiphertext; ConcreteInnerEncryptorTest.DoesntEncryptWhenTooLarge; ConcreteInnerEncryptorTest.EncryptionIsFixedSize. Assertion/mocking density: EXPECT_EQ x7, EXPECT_THROW x1.
