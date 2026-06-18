# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsTest.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 42 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Macros/constants: `MESSMER_FSPP_FSTEST_FSTEST_H_`, `FSPP_ADD_FILESYTEM_TESTS`. Important declarations or call sites include `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDeviceTest_One,             FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDeviceTest_Two,             FIXTURE);  \`; `INSTANTIATE_NODE_TEST_SUITE(   FS_NAME, FsppDeviceTest_Timestamps,      FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDirTest,                    FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppDirTest_Timestamps,         FIXTURE);  \`; `INSTANTIATE_NODE_TEST_SUITE(   FS_NAME, FsppDirTest_Timestamps_Entries, FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppFileTest,                   FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppFileTest_Timestamps,        FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppSymlinkTest,                FIXTURE);  \`; `INSTANTIATE_TYPED_TEST_SUITE_P(FS_NAME, FsppSymlinkTest_Timestamps,     FIXTURE);  \`. CMake commands used here include `INSTANTIATE_TYPED_TEST_SUITE_P`, `INSTANTIATE_NODE_TEST_SUITE`. Primary includes/dependencies visible in the file include `testutils/FileSystemTest.h`, `FsppDeviceTest.h`, `FsppDirTest.h`, `FsppFileTest.h`, `FsppSymlinkTest.h`, `FsppNodeTest_Rename.h`, `FsppNodeTest_Stat.h`, `FsppOpenFileTest.h`, `FsppDeviceTest_Timestamps.h`, `FsppNodeTest_Timestamps.h`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are `testutils/FileSystemTest.h`, `FsppDeviceTest.h`, `FsppDirTest.h`, `FsppFileTest.h`, `FsppSymlinkTest.h`, `FsppNodeTest_Rename.h`, `FsppNodeTest_Stat.h`, `FsppOpenFileTest.h`.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.
