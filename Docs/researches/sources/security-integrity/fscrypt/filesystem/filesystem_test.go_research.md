# sources/security-integrity/fscrypt/filesystem/filesystem_test.go

## Purpose
This file tests fscrypt metadata setup, persistence, validation, linked protectors, ownership protections, and safe file reading against a real test mount supplied by `util.TestRoot`.

## Important APIs, Types, and Functions
Helpers construct fake protectors and policies with real wrapped key data: `getFakeProtector`, `getFakeLoginProtector`, `getFakePolicy`, `getSetupMount`, `getTwoSetupMounts`, `cleanupTwoMounts`, and `createFile`. Tests cover `Setup`, `RemoveAllMetadata`, setup through `.fscrypt` symlinks, setup modes, `CheckSetup`, `AddProtector`, `AddPolicy`, `GetPolicy`, `GetRegularProtector`, linked protectors, and `readMetadataFileSafe`.

## Control Flow
Most tests obtain a test mount, run `Setup(WorldWritable)`, perform metadata operations, and defer cleanup through `RemoveAllMetadata`. Negative tests mutate metadata fields after a successful control case to assert validation fails. The safe-read test creates files with varying types and sizes and checks expected error classes.

## State and Persistence
Tests write real `.fscrypt` metadata under the configured test filesystem and remove it afterward. Temporary directories and fake mount subdirectories are used for symlink and linked-protector scenarios. Package-level fake keys are created once for wrapping fixtures.

## Dependencies and Integration Points
Depends on `crypto.Wrap`, metadata structs, `proto.Equal`, `unix.Mkfifo`, and test support in `util.TestRoot`. It validates interactions between filesystem persistence and metadata validators rather than only unit-level helpers.

## Risks
Tests require a suitable test root and can be skipped or fail depending on permissions, root status, and filesystem capabilities. Because they mutate `.fscrypt`, a misconfigured `TestRoot` could affect real metadata. Several behaviors vary for root versus non-root ownership checks.

## Test Signals
Strong coverage exists for setup semantics, metadata round trips, validation failures, mode `0600`, linked-protector lookup, login protector UID spoofing, and TOCTOU-oriented safe reading. It does not exhaustively test write crash consistency or all possible malformed protobuf contents.
