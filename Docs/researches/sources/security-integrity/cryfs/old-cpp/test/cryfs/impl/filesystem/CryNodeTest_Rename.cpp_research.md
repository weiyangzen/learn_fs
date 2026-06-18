# sources/security-integrity/cryfs/old-cpp/test/cryfs/impl/filesystem/CryNodeTest_Rename.cpp

Purpose: This file tests CryFS node rename behavior for files, directories, and symlinks, including block cleanup and parent pointer updates.

Important APIs/types/functions: Includes: gtest/gtest.h, testutils/CryTestBase.h, cryfs/impl/filesystem/CryOpenFile.h. Classes/fixtures: CryNodeTest_Rename. Helper functions: none visible. Direct tests: CryNodeTest_Rename.DoesntLeaveBlocksOver; CryNodeTest_Rename.Overwrite_DoesntLeaveBlocksOver; CryNodeTest_Rename.UpdatesParentPointers_File; CryNodeTest_Rename.UpdatesParentPointers_Dir; CryNodeTest_Rename.UpdatesParentPointers_Symlink.

Control flow: Fixture setup creates or loads a CryFS config/device, test code performs filesystem operations, and assertions verify node state, file contents, config bytes, or thrown errno exceptions.

State and persistence behavior: It uses `CryTestBase` to create real encrypted filesystem nodes in a temp basedir. Persistent state includes directory entries, node metadata, file blocks, and symlink targets.

Dependencies and integration points: It integrates CryFS filesystem objects with config loading, key providers, fake home/local-state helpers, cpp-utils temp files, and fspp interface expectations.

Risks: Rename bugs can orphan blocks, lose data, or leave parent pointers inconsistent after move/overwrite operations.

Test signals: Primary signals are CryNodeTest_Rename.DoesntLeaveBlocksOver; CryNodeTest_Rename.Overwrite_DoesntLeaveBlocksOver; CryNodeTest_Rename.UpdatesParentPointers_File; CryNodeTest_Rename.UpdatesParentPointers_Dir; CryNodeTest_Rename.UpdatesParentPointers_Symlink. Assertion/mocking density: EXPECT_EQ x4, EXPECT_TRUE x3.
