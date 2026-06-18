# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigFileTest.cpp

Purpose: This file tests encrypted config-file creation, loading, saving, wrong-password failure, and persistence of individual `CryConfig` fields.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/CryConfigFile.h, cpp-utils/tempfile/TempFile.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h, ../../impl/testutils/FakeCryKeyProvider.h, boost/optional/optional_io.hpp. Classes/fixtures: CryConfigFileTest. Helper functions: CryConfigFileTest, Config, CreateAndLoadEmpty, Create, Load, CreateWithCipher. Direct tests: CryConfigFileTest.DoesntLoadIfWrongPassword; CryConfigFileTest.RootBlob_Init; CryConfigFileTest.RootBlob_CreateAndLoad; CryConfigFileTest.RootBlob_SaveAndLoad; CryConfigFileTest.EncryptionKey_Init; CryConfigFileTest.EncryptionKey_CreateAndLoad; CryConfigFileTest.EncryptionKey_SaveAndLoad; CryConfigFileTest.Cipher_Init; CryConfigFileTest.Cipher_CreateAndLoad; CryConfigFileTest.Cipher_SaveAndLoad; CryConfigFileTest.Version_Init; CryConfigFileTest.Version_CreateAndLoad.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It writes real temporary config files and reloads them with fake key providers. Persistent fields under test include root blob, encryption key, cipher, version, created/opened versions, filesystem ID, block size, and integrity policy.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Serialization and encryption bugs here affect every mounted filesystem because config files are the root of key and format metadata.

Test signals: Primary signals are CryConfigFileTest.DoesntLoadIfWrongPassword; CryConfigFileTest.RootBlob_Init; CryConfigFileTest.RootBlob_CreateAndLoad; CryConfigFileTest.RootBlob_SaveAndLoad; CryConfigFileTest.EncryptionKey_Init; CryConfigFileTest.EncryptionKey_CreateAndLoad; CryConfigFileTest.EncryptionKey_SaveAndLoad; CryConfigFileTest.Cipher_Init. Assertion/mocking density: EXPECT_EQ x20.
