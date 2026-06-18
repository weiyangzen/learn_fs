# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_RenameNested.cpp

Purpose: This file parameterizes nested rename paths to verify valid moves succeed and invalid self/descendant moves fail with FUSE errno semantics.

Important APIs/types/functions: Includes: gtest/gtest.h, testutils/CryTestBase.h, cryfs/impl/filesystem/CryDir.h, cryfs/impl/filesystem/CryFile.h, cryfs/impl/filesystem/CryOpenFile.h, fspp/fs_interface/FuseErrnoException.h, boost/algorithm/string/predicate.hpp. Classes/fixtures: CryNodeTest_RenameNested. Helper functions: SourceDirs, DestDirs, CreateDirs, create_path_if_not_exists, expect_rename_succeeds, expect_rename_fails. Direct tests: CryNodeTest_RenameNested.Rename.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It creates source/destination directory trees through `CryTestBase`; state is temp CryFS node hierarchy and parent-child metadata.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: Nested rename is prone to cycles, partial moves, and path normalization mistakes.

Test signals: Primary signals are CryNodeTest_RenameNested.Rename. Assertion/mocking density: ASSERT_EQ x1, ASSERT_TRUE x2, ASSERT_FALSE x2.
