# sources/storage-engines/leveldb/util/env_windows_test_helper.h

## Purpose
`env_windows_test_helper.h` exposes a private mmap-limit setter for Windows env tests.

## Important APIs, Types, and Functions
`EnvWindowsTestHelper` declares private static `SetReadOnlyMMapLimit`, friended to `CorruptionTest` and `EnvWindowsTest`.

## Control Flow
Tests call the setter before default env singleton construction; the implementation asserts pre-initialization in debug builds.

## State, Dependencies, and Integration
The header controls `g_mmap_limit` in `env_windows.cc` without exposing it through public env APIs.

## Risks and Test Signals
Late calls are unsafe outside debug detection. Windows open-on-read testing depends on this hook.
