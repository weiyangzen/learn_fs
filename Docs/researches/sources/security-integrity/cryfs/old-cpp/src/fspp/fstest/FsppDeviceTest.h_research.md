# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 471 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ConcreteFileSystemTestFixture`, `FsppDeviceTest`, `FsppDeviceTest_One`, `FsppDeviceTest_Two`. Macros/constants: `MESSMER_FSPP_FSTEST_FSPPDEVICETEST_H_`. Important declarations or call sites include `void InitDirStructure() {`; `this->LoadDir("/")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createSymlink("mysymlink", "/symlink/target", fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("mydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("myemptydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile2", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createSymlink("mysymlink", "/symlink/target", fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createDir("mysubdir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir/mysubdir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`. CMake commands used here include `TYPED_TEST_SUITE_P`, `TYPED_TEST_P`, `EXPECT_THROW`, `EXPECT_EQ`, `REGISTER_TYPED_TEST_SUITE_P`. Primary includes/dependencies visible in the file include `fspp/fs_interface/FuseErrnoException.h`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are `fspp/fs_interface/FuseErrnoException.h`.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.
