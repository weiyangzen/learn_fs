# sources/security-integrity/fscrypt/metadata/policy_test.go

## Purpose
This test file validates setting and reading kernel fscrypt policies on a test filesystem and error behavior for invalid targets or descriptors.

## Important APIs, Types, and Functions
Fixtures include `goodV1Policy`, `goodV2Policy`, and encryption option structs. Helpers `createTestDirectory`, `createTestFile`, and `requireV2PolicySupport` prepare test directories and gate v2 behavior. Tests cover empty directories, nonempty directories, regular files, bad descriptors, reading policies, unencrypted directories, and v2 policy without key.

## Control Flow
Tests create directories under `util.TestRoot`, call `SetPolicy`, use `GetPolicy` for round trips, and remove temporary directories. Negative cases assert error presence rather than exact kernel error for every scenario.

## State and Persistence
Tests set real fscrypt policies on temporary directories and then remove the directory tree. Once a policy is set, it is a filesystem-level state until deletion.

## Dependencies and Integration Points
Depends on Linux fscrypt support in the test filesystem, `unix` ioctl constants, and `proto.Equal`. It validates behavior used by encrypt actions and metadata support checks.

## Risks
Environment-sensitive tests may skip or fail depending on kernel, filesystem feature flags, root status, and configured test root. Tests do not cover all v2 success paths, which are handled in keyring tests.

## Test Signals
The file confirms core kernel policy interactions and validates important user-facing error cases around nonempty dirs, regular files, malformed descriptors, and missing v2 keys.
