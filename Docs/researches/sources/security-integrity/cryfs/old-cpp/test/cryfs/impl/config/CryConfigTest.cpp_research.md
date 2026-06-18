# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigTest.cpp

Purpose: This file tests the in-memory `CryConfig` data model and its serialize/deserialize behavior for all config fields.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/CryConfig.h, cpp-utils/data/DataFixture.h, cpp-utils/pointer/unique_ref_boost_optional_gtest_workaround.h. Classes/fixtures: CryConfigTest. Helper functions: SaveAndLoad. Direct tests: CryConfigTest.RootBlob_Init; CryConfigTest.RootBlob; CryConfigTest.RootBlob_AfterMove; CryConfigTest.RootBlob_AfterCopy; CryConfigTest.RootBlob_AfterSaveAndLoad; CryConfigTest.EncryptionKey_Init; CryConfigTest.EncryptionKey; CryConfigTest.EncryptionKey_AfterMove; CryConfigTest.EncryptionKey_AfterCopy; CryConfigTest.EncryptionKey_AfterSaveAndLoad; CryConfigTest.Cipher_Init; CryConfigTest.Cipher.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is mostly in-memory, with save/load round trips through serialized config data to verify persistence semantics after copy and move operations.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Optional-field and move/copy behavior must remain stable because config file code stores and retrieves these values across versions.

Test signals: Primary signals are CryConfigTest.RootBlob_Init; CryConfigTest.RootBlob; CryConfigTest.RootBlob_AfterMove; CryConfigTest.RootBlob_AfterCopy; CryConfigTest.RootBlob_AfterSaveAndLoad; CryConfigTest.EncryptionKey_Init; CryConfigTest.EncryptionKey; CryConfigTest.EncryptionKey_AfterMove. Assertion/mocking density: EXPECT_EQ x41.
