# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/crypto/CryConfigEncryptorFactoryTest.cpp

Purpose: This file tests the encryptor factory that builds config encryptors from a CryFS key provider and validates same/new encryptor decryptability and wrong-key failure.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/crypto/CryConfigEncryptorFactory.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, ../../../impl/testutils/FakeCryKeyProvider.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h. Classes/fixtures: CryConfigEncryptorFactoryTest. Helper functions: none visible. Direct tests: CryConfigEncryptorFactoryTest.EncryptAndDecrypt_SameEncryptor; CryConfigEncryptorFactoryTest.EncryptAndDecrypt_NewEncryptor; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey_EmptyData; CryConfigEncryptorFactoryTest.DoesntDecryptInvalidData.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It uses in-memory plaintext/ciphertext and fake key providers; no durable state is written.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Factory/key-provider wiring errors can make existing configs undecryptable or accept corrupted data.

Test signals: Primary signals are CryConfigEncryptorFactoryTest.EncryptAndDecrypt_SameEncryptor; CryConfigEncryptorFactoryTest.EncryptAndDecrypt_NewEncryptor; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey; CryConfigEncryptorFactoryTest.DoesntDecryptWithWrongKey_EmptyData; CryConfigEncryptorFactoryTest.DoesntDecryptInvalidData. Assertion/mocking density: EXPECT_EQ x5.
