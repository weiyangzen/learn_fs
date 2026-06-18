# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDeviceTest_Timestamps.h

## Purpose
Defines reusable typed GoogleTest suites that exercise fspp device, directory, file, symlink, rename, stat, and timestamp behavior against filesystem fixtures. This specific file has 50 source lines under `sources/security-integrity/cryfs/old-cpp/src/fspp/fstest` and participates in the old CryFS C++ security/integrity code path.

## Important APIs, Types, and Functions
Types/classes: `ConcreteFileSystemTestFixture`, `FsppDeviceTest_Timestamps`. Macros/constants: `MESSMER_FSPP_FSTEST_FSPPDEVICETEST_TIMESTAMPS_H_`. Important declarations or call sites include `void Test_Load_While_Loaded() {`; `auto node = this->CreateNode("/mynode");`; `this->device->Load("/mynode");`; `this->EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS("/mynode", operation(), {this->ExpectDoesntUpdateAnyTimestamps});`; `void Test_Load_While_Not_Loaded() {`; `auto node = this->CreateNode("/mynode");`; `oldStat = this->stat(*node);`; `this->ensureNodeTimestampsAreOld(oldStat);`; `this->device->Load("/myfile");`; `auto node = this->device->Load("/mynode");`. CMake commands used here include `EXPECT_EQ`, `REGISTER_NODE_TEST_SUITE`. Primary includes/dependencies visible in the file include `testutils/TimestampTestUtils.h`.

## Control Flow
Each typed test constructs fixture files or directories, performs fspp API calls, and asserts POSIX-like results, errors, children, or timestamp changes through shared fixture utilities.

## State and Persistence Behavior
Tests create fixture filesystem state through the fixture device and assert behavior; no production persistence is implemented in these headers.

## Dependencies and Integration Points
Integrates with GoogleTest typed suites, fspp node/device interfaces, errno exceptions, and fixture utilities; visible includes are `testutils/TimestampTestUtils.h`.

## Risks and Edge Cases
These tests assume POSIX-like semantics and fixture correctness. Flaky timestamp granularity or filesystem-specific behavior can cause false failures.

## Test Signals
These headers are themselves test suites; instantiate them against filesystem fixtures and watch for POSIX errno, directory listing, rename/stat, and timestamp regressions.

## File-Specific Notes
- This is reusable test code rather than production code; its integration point is the fixture type passed to GoogleTest typed suites.
