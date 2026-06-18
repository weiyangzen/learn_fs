# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/LocalStateMetadataTest.cpp

Purpose: This file tests `LocalStateMetadata` persistence, loading, updating, and lookup behavior for CryFS local state.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/localstate/LocalStateMetadata.h, cpp-utils/tempfile/TempDir.h, fstream, cpp-utils/data/DataFixture.h. Classes/fixtures: LocalStateMetadataTest. Helper functions: none visible. Direct tests: LocalStateMetadataTest.myClientId_ValueIsConsistent; LocalStateMetadataTest.myClientId_ValueIsRandomForNewClient; LocalStateMetadataTest.myClientId_TakesLegacyValueIfSpecified; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithSameKey_thenDoesntCrash; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithDifferentKey_thenCrashes.

Control flow: The fixture creates a temporary local-state directory, performs metadata reads/writes through production local-state APIs, and asserts success or failure for specific basedir/filesystem-ID combinations.

State and persistence behavior: It uses temp directories and fake home state to persist local-state files, then reloads or updates metadata values.

Dependencies and integration points: It integrates `LocalStateDir`, metadata wrappers, `CryConfig` filesystem IDs, temp directories, and fake home-directory behavior.

Risks: Local-state corruption or path identity drift affects filesystem safety checks and user-specific metadata.

Test signals: Primary signals are LocalStateMetadataTest.myClientId_ValueIsConsistent; LocalStateMetadataTest.myClientId_ValueIsRandomForNewClient; LocalStateMetadataTest.myClientId_TakesLegacyValueIfSpecified; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithSameKey_thenDoesntCrash; LocalStateMetadataTest.encryptionKeyHash_whenLoadingWithDifferentKey_thenCrashes. Assertion/mocking density: EXPECT_EQ x2, EXPECT_THROW x1, EXPECT_NE x1.
