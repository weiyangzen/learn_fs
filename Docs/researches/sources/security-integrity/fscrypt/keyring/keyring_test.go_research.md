# sources/security-integrity/fscrypt/keyring/keyring_test.go

## Purpose
This integration test file verifies kernel keyring operations across user keyrings, filesystem keyrings for v1 policies, and filesystem keyrings for v2 policies.

## Important APIs, Types, and Functions
Helpers include `ConstReader`, `makeKey`, `assertKeyStatus`, `getTestMount`, `getTestMountV2`, `requireRoot`, `getNonRootUsers`, `getOptionsForFsKeyringUsers`, and `testAddAndRemoveKey`. Tests cover user keyring, fs keyring v1, v2 policy keys, cross-user removal, multiple user claims, wrong v2 descriptors, bad mounts, and root all-user removal.

## Control Flow
Common tests add a fake policy key, assert present status, remove it, assert absent status, confirm removing again returns `ErrKeyNotPresent`, assert duplicate add succeeds, and assert wrong-length keys fail. V2 tests use additional users and root to validate kernel claim semantics.

## State and Persistence
State is in live kernel keyrings. Tests can add and remove keys for real users and require a test mount. Some paths require root and configured users with UIDs starting at 1000.

## Dependencies and Integration Points
Depends on `filesystem.GetMount`, `util.TestRoot`, crypto descriptor derivation, metadata key lengths, and Linux fscrypt kernel support. It validates the real behavior used by policy provisioning and PAM session handling.

## Risks
Tests are environment-sensitive and skip when root, test users, filesystem keyring support, or test mount are unavailable. Failed cleanup could leave keys in kernel keyrings until session/user keyring cleanup or explicit removal.

## Test Signals
The tests strongly signal expected kernel-keyring semantics, especially v2 user-claim isolation and all-user removal. They do not mock ioctl failures beyond nonexistent mount paths.
