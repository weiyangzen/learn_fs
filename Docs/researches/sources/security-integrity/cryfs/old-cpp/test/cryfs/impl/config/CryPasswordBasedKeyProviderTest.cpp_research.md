# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/config/CryPasswordBasedKeyProviderTest.cpp

Purpose: This file tests the interactive password-based key provider, including double-entry confirmation for new filesystems and single password prompt for existing filesystems.

Important APIs/types/functions: Includes: cryfs/impl/config/CryPasswordBasedKeyProvider.h, gmock/gmock.h, ../../impl/testutils/MockConsole.h, cpp-utils/data/DataFixture.h. Classes/fixtures: MockCallable, MockKDF, CryPasswordBasedKeyProviderTest. Helper functions: CryPasswordBasedKeyProviderTest. Direct tests: CryPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem.

Control flow: The test fixture prepares console/key/config dependencies, invokes the production config or crypto API, and then validates either returned values, exceptions/load errors, mock expectations, or serialized round trips.

State and persistence behavior: State consists of mock console password answers, mock KDF calls, and deterministic derived key data. No files are persisted.

Dependencies and integration points: The file integrates Google Test/Mock with CryFS config classes, cpp-utils data/KDF/crypto helpers, temp files, fake home directories, and local-state/version helpers as needed by the target under test.

Risks: Prompt sequencing and retry behavior are security-sensitive because weak or mismatched password handling affects filesystem access.

Test signals: Primary signals are CryPasswordBasedKeyProviderTest.requestKeyForNewFilesystem; CryPasswordBasedKeyProviderTest.requestKeyForExistingFilesystem. Assertion/mocking density: EXPECT_EQ x4, EXPECT_CALL x6.
