# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 306 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ConcreteFileSystemTestFixture`, `FsppDirTest`, `Entry`. Macros/constants: `MESSMER_FSPP_FSTEST_FSPPDIRTEST_H_`. Important declarations or call sites include `void InitDirStructure() {`; `this->LoadDir("/")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("mydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/")->createDir("myemptydir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createAndOpenFile("myfile2", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir")->createDir("mysubdir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir/mysubdir")->createAndOpenFile("myfile", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `this->LoadDir("/mydir/mysubdir")->createDir("mysubsubdir", this->MODE_PUBLIC, fspp::uid_t(0), fspp::gid_t(0));`; `void EXPECT_CHILDREN_ARE(const boost::filesystem::path &path, const std::initializer_list<fspp::Dir::Entry> expected) {`. CMake commands used here include `EXPECT_CHILDREN_ARE`, `EXPECT_UNORDERED_EQ`, `EXPECT_EQ`, `for`, `removeOne`, `if`, `EXPECT_TRUE`, `TYPED_TEST_SUITE_P`, `TYPED_TEST_P`, `FileEntry`, `DirEntry`, `EXPECT_ANY_THROW`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are the containing CryFS build/module.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.
