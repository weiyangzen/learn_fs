# sources/security-integrity/fscrypt/keyring/keyring.go

## Purpose
`keyring.go` provides the package-level API for adding, removing, and querying fscrypt policy keys while selecting between deprecated user keyrings and modern filesystem keyrings.

## Important APIs, Types, and Functions
Public errors include `ErrKeyAddedByOtherUsers`, `ErrKeyFilesOpen`, `ErrKeyNotPresent`, and `ErrV2PoliciesUnsupported`. `Options` selects mount, target user, and v1 filesystem-keyring preference. Public functions are `AddEncryptionKey`, `RemoveEncryptionKey`, and `GetEncryptionKeyStatus`. `KeyStatus` enumerates absent/present/busy/other-user states.

## Control Flow
`shouldUseFsKeyring` distinguishes v1 descriptors by hex-encoded `FSCRYPT_KEY_DESCRIPTOR_SIZE`; v1 can use user keyring unless configured otherwise, while v2 always requires filesystem keyring support. `AddEncryptionKey` validates policy key length then delegates to `fsAddEncryptionKey` or `userAddKey`. Remove and status perform the same dispatch and normalize results.

## State and Persistence
No direct state is stored here. It routes operations that affect kernel keyrings. Options are caller-owned and include the target mount/user.

## Dependencies and Integration Points
Integrates crypto key lengths, metadata constants, mount filesystem type, user identity, and both implementation files. `actions.Policy` and PAM provisioning call this layer to provision or deprovision policy keys.

## Risks
Descriptor length is the switch between v1 and v2 semantics; malformed but correctly sized descriptors pass to lower layers for decoding. v2 policies cannot work without filesystem-keyring support. User-keyring fallback for v1 preserves legacy behavior but has different lifetime and privilege semantics.

## Test Signals
`keyring_test.go` exercises dispatch through user keyring, fs keyring for v1, and fs keyring for v2, including invalid key length, duplicate add, absent remove, and status transitions.
