# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPresetPasswordBasedKeyProviderTest.cpp

Purpose: This file tests the noninteractive preset-password key provider for new and existing filesystems.

Important APIs/types/functions: Includes: cryfs/impl/config/CryPresetPasswordBasedKeyProvider.h, gmock/gmock.h, ../../impl/testutils/MockConsole.h, cpp-utils/data/DataFixture.h. Classes/fixtures: MockKDF. Helper functions: none visible. Direct tests: CryPresetPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPresetPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State is deterministic password input and mock KDF output; no console prompts or files are used.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: The provider bypasses confirmation prompts by design, so tests must ensure it still derives the same key material used by the interactive path.

Test signals: Primary signals are CryPresetPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPresetPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem. Assertion/mocking density: EXPECT_EQ x4, EXPECT_CALL x2.
