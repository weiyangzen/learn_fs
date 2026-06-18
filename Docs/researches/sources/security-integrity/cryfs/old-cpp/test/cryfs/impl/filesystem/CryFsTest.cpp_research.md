# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryFsTest.cpp

Purpose: This file tests that a newly created CryFS root directory can be reloaded after closing and that loading an existing filesystem does not mutate the config file.

Important APIs/types/functions: Includes: gtest/gtest.h, cpp-utils/tempfile/TempDir.h, cpp-utils/tempfile/TempFile.h, cpp-utils/pointer/cast.h, cryfs/impl/filesystem/CryDevice.h, cryfs/impl/filesystem/CryDir.h, cryfs/impl/filesystem/CryFile.h, cryfs/impl/filesystem/CryOpenFile.h, ../testutils/MockConsole.h, plus 5 more. Classes/fixtures: CryFsTest. Helper functions: CryFsTest, loadOrCreateConfig, failOnIntegrityViolation. Direct tests: CryFsTest.CreatedRootdirIsLoadableAfterClosing; CryFsTest.LoadingFilesystemDoesntModifyConfigFile.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It uses temp basedir/config paths, fake home directory, mock console, `CryConfigLoader`, and `CryDevice`. The config file contents are persistent test state and are compared before/after loading.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: A load path that rewrites configs unnecessarily can cause noisy metadata changes or compatibility problems.

Test signals: Primary signals are CryFsTest.CreatedRootdirIsLoadableAfterClosing; CryFsTest.LoadingFilesystemDoesntModifyConfigFile. Assertion/mocking density: EXPECT_EQ x1, EXPECT_TRUE x1.
