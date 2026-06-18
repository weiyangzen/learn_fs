# sources/storage-engines/leveldb/util/env_windows_test.cc

## Purpose
`env_windows_test.cc` validates Windows env fallback from mmap-backed random access to ordinary file reads.

## Important APIs, Types, and Functions
`EnvWindowsTest`, static `SetFileLimits`, and `TestOpenOnRead` are defined. `main` sets the mmap limit before initializing gtest.

## Control Flow
The test writes alphabet data to a temp file, opens more random-access files than the configured mmap limit, reads one byte at each offset, verifies content, deletes objects, and removes the file.

## State, Dependencies, and Integration
It uses `EnvWindowsTestHelper` before `Env::Default()` and depends on real Windows file APIs via the default env.

## Risks and Test Signals
The test proves resource exhaustion falls back to `WindowsRandomAccessFile`. It does not cover Windows locking, rename replacement, or close-on-exec analogs.
