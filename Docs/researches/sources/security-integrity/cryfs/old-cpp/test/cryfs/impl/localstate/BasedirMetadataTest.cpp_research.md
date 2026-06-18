# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/localstate/BasedirMetadataTest.cpp

Purpose: This file tests basedir-to-filesystem-ID metadata validation in the CryFS local-state directory.

Important APIs/types/functions: Includes: gtest/gtest.h, cryfs/impl/localstate/BasedirMetadata.h, cryfs/impl/localstate/LocalStateDir.h, cryfs/impl/config/CryConfig.h, cpp-utils/tempfile/TempDir.h, ../testutils/TestWithFakeHomeDirectory.h. Classes/fixtures: BasedirMetadataTest. Helper functions: none visible. Direct tests: BasedirMetadataTest.givenEmptyState_whenCalled_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledForDifferentBasedir_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithDifferentId_thenFails; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithDifferentId_thenFails.

Control flow: The fixture creates a temporary local-state directory, performs metadata reads/writes through production local-state APIs, and asserts success or failure for specific basedir/filesystem-ID combinations.

State and persistence behavior: It writes local-state metadata under a temp fake home and compares behavior for empty state, same basedir/same ID, same basedir/different ID, and updated basedir metadata.

Dependencies and integration points: It integrates `LocalStateDir`, metadata wrappers, `CryConfig` filesystem IDs, temp directories, and fake home-directory behavior.

Risks: Incorrect basedir metadata can allow accidentally mounting a basedir with the wrong filesystem identity or can reject valid moves.

Test signals: Primary signals are BasedirMetadataTest.givenEmptyState_whenCalled_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledForDifferentBasedir_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithBasedir_whenCalledWithDifferentId_thenFails; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithSameId_thenSucceeds; BasedirMetadataTest.givenStateWithUpdatedBasedir_whenCalledWithDifferentId_thenFails. Assertion/mocking density: EXPECT_TRUE x4, EXPECT_FALSE x2.
