# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryConfigLoaderTest.cpp

Purpose: This file exercises load-or-create behavior for CryFS configs, including wrong passwords, cipher mismatch, config mutation on open, version upgrade checks, filesystem ID/local-state validation, and access modes.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/config/CryConfigLoader.h, cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, ../../impl/testutils/MockConsole.h, ../../impl/testutils/TestWithFakeHomeDirectory.h, cpp-utils/tempfile/TempFile.h, cpp-utils/random/Random.h, cpp-utils/crypto/symmetric/ciphers.h, cpp-utils/data/DataFixture.h, plus 6 more. Classes/fixtures: FakeRandomGenerator, CryConfigLoaderTest. Helper functions: FakeRandomGenerator, _get, keyProvider, loader, Create, LoadOrCreate, Load, expectLoadingModifiesFile, expectLoadingDoesntModifyFile, CreateWithRootBlob, plus 8 more. Direct tests: CryConfigLoaderTest.CreatesNewIfNotExisting; CryConfigLoaderTest.DoesntCrashIfExisting; CryConfigLoaderTest.DoesntLoadIfWrongPassword; CryConfigLoaderTest.DoesntLoadIfDifferentCipher; CryConfigLoaderTest.DoesntLoadIfDifferentCipher_Noninteractive; CryConfigLoaderTest.DoesLoadIfSameCipher; CryConfigLoaderTest.DoesLoadIfSameCipher_Noninteractive; CryConfigLoaderTest.RootBlob_Load; CryConfigLoaderTest.RootBlob_Create; CryConfigLoaderTest.EncryptionKey_Load; CryConfigLoaderTest.EncryptionKey_Load_whenKeyChanged_thenFails; CryConfigLoaderTest.EncryptionKey_Create.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: It owns a temporary config file and local-state directory under a fake home, writes configs with controlled random encryption keys, mutates on-disk config data, and compares file bytes before/after load.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: This is a high-blast-radius loader: incorrect behavior can corrupt configs, miss incompatible versions, or wrongly accept a filesystem from another basedir.

Test signals: Primary signals are CryConfigLoaderTest.CreatesNewIfNotExisting; CryConfigLoaderTest.DoesntCrashIfExisting; CryConfigLoaderTest.DoesntLoadIfWrongPassword; CryConfigLoaderTest.DoesntLoadIfDifferentCipher; CryConfigLoaderTest.DoesntLoadIfDifferentCipher_Noninteractive; CryConfigLoaderTest.DoesLoadIfSameCipher; CryConfigLoaderTest.DoesLoadIfSameCipher_Noninteractive; CryConfigLoaderTest.RootBlob_Load. Assertion/mocking density: EXPECT_EQ x19, ASSERT_EQ x3, EXPECT_THROW x1, EXPECT_TRUE x15, EXPECT_FALSE x2, EXPECT_CALL x9, EXPECT_NE x3, ASSERT_TRUE x2.
