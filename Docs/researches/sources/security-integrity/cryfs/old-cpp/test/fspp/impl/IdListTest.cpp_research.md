# sources/security-integrity/cryfs/old-cpp/test/fspp/impl/IdListTest.cpp

Purpose: This file tests `IdList`, a generic ID-to-object container used by fspp internals.

Important APIs/types/functions: Includes: gtest/gtest.h, fspp/impl/IdList.h, stdexcept. Classes/fixtures: MyObj. Helper functions: MyObj, add, check, checkConst. Direct tests: IdListTest.EmptyList1; IdListTest.EmptyList2; IdListTest.InvalidId; IdListTest.GetRemovedItemOnEmptyList; IdListTest.GetRemovedItemOnNonEmptyList; IdListTest.RemoveOnEmptyList1; IdListTest.RemoveOnEmptyList2; IdListTest.RemoveInvalidId; IdListTest.Add1AndGet; IdListTest.Add2AndGet; IdListTest.Add3AndGet; IdListTest.Add3AndConstGet.

Control flow: Tests add/open objects, retrieve them by ID, remove/close them, and assert object identity or thrown exceptions for invalid/removed IDs.

State and persistence behavior: Runtime state is the ID list, object ownership, active/removed slots, and exception behavior for invalid IDs. There is no disk persistence.

Dependencies and integration points: The container under test supports FUSE adapter handle management, so it integrates with open/close/read/write operation paths indirectly.

Risks: ID reuse and invalid-ID handling are foundational for higher-level FUSE handle maps.

Test signals: Primary signals are IdListTest.EmptyList1; IdListTest.EmptyList2; IdListTest.InvalidId; IdListTest.GetRemovedItemOnEmptyList; IdListTest.GetRemovedItemOnNonEmptyList; IdListTest.RemoveOnEmptyList1; IdListTest.RemoveOnEmptyList2; IdListTest.RemoveInvalidId. Assertion/mocking density: EXPECT_EQ x2.
