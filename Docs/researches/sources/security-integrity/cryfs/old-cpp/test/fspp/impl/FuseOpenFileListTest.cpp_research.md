# sources/security-integrity/cryfs/old-cpp/test/fspp/impl/FuseOpenFileListTest.cpp

Purpose: This file tests `FuseOpenFileList`, the table that maps FUSE file-handle IDs to live `OpenFile` objects.

Important APIs/types/functions: Includes: gtest/gtest.h, gmock/gmock.h, fspp/impl/FuseOpenFileList.h, stdexcept. Classes/fixtures: MockOpenFile. Helper functions: MockOpenFile, open, check. Direct tests: FuseOpenFileListTest.EmptyList1; FuseOpenFileListTest.EmptyList2; FuseOpenFileListTest.InvalidId; FuseOpenFileListTest.Open1AndGet; FuseOpenFileListTest.Open2AndGet; FuseOpenFileListTest.Open3AndGet; FuseOpenFileListTest.GetClosedItemOnEmptyList; FuseOpenFileListTest.GetClosedItemOnNonEmptyList; FuseOpenFileListTest.CloseOnEmptyList1; FuseOpenFileListTest.CloseOnEmptyList2; FuseOpenFileListTest.RemoveInvalidId.

Control flow: Tests add/open objects, retrieve them by ID, remove/close them, and assert object identity or thrown exceptions for invalid/removed IDs.

State and persistence behavior: Runtime state is the open-file list, generated IDs, stored unique pointers, and removed/closed slots. There is no disk persistence.

Dependencies and integration points: The container under test supports FUSE adapter handle management, so it integrates with open/close/read/write operation paths indirectly.

Risks: Bad handle allocation/removal can return wrong open files to later FUSE calls or leak handles.

Test signals: Primary signals are FuseOpenFileListTest.EmptyList1; FuseOpenFileListTest.EmptyList2; FuseOpenFileListTest.InvalidId; FuseOpenFileListTest.Open1AndGet; FuseOpenFileListTest.Open2AndGet; FuseOpenFileListTest.Open3AndGet; FuseOpenFileListTest.GetClosedItemOnEmptyList; FuseOpenFileListTest.GetClosedItemOnNonEmptyList. Assertion/mocking density: EXPECT_EQ x2, EXPECT_TRUE x1, EXPECT_FALSE x1.
