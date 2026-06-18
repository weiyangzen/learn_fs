# sources/storage-engines/leveldb/util/env_posix_test_helper.h

## Purpose
`env_posix_test_helper.h` exposes private POSIX env tuning hooks only to tests.

## Important APIs, Types, and Functions
`EnvPosixTestHelper` has private static `SetReadOnlyFDLimit` and `SetReadOnlyMMapLimit`, with `EnvPosixTest` as a friend.

## Control Flow
Tests call these setters before `Env::Default()` creates the singleton. The implementation asserts the env is not initialized in debug builds.

## State, Dependencies, and Integration
The header has no state itself; it controls global variables in `env_posix.cc`. It integrates with `env_posix_test.cc` and avoids exposing test-only controls publicly.

## Risks and Test Signals
Calling after env initialization has no safe effect and is guarded only by debug assertions. Tests depend on this to force open-on-read behavior deterministically.
