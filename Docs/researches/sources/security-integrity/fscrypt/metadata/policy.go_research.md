# sources/security-integrity/fscrypt/metadata/policy.go

## Purpose
`policy.go` interfaces with Linux fscrypt policy ioctls to get, set, and support-check encryption policies on files or directories.

## Important APIs, Types, and Functions
Public errors include `ErrEncryptionNotSupported`, `ErrEncryptionNotEnabled`, `ErrAlreadyEncrypted`, `ErrBadEncryptionOptions`, `ErrDirectoryNotOwned`, `ErrLockedRegularFile`, and `ErrNotEncrypted`. Public functions are `GetPolicy`, `SetPolicy`, and `CheckSupport`. Internal helpers map kernel policy structs and flags: `getPolicyIoctl`, `setPolicy`, `flagsToPadding`, `buildV1PolicyData`, `buildV2PolicyData`, `shouldUseDirectKeyFlag`, `buildPolicyFlags`, `setV1Policy`, and `setV2Policy`.

## Control Flow
`GetPolicy` opens the path, tries `FS_IOC_GET_ENCRYPTION_POLICY_EX`, falls back to the legacy ioctl on `ENOTTY`, maps kernel errors to package errors, and converts v1 or v2 structs into `PolicyData`. `SetPolicy` opens the directory, validates metadata, decodes the descriptor, dispatches to v1 or v2 policy setting, disambiguates old-kernel `EINVAL`, and maps errors to domain-specific messages. `CheckSupport` sets an intentionally invalid policy and interprets kernel errors to infer encryption support/enabled state.

## State and Persistence
Successful `SetPolicy` persists an encryption policy on the target directory in the filesystem through kernel ioctls and syncs the file descriptor. No `.fscrypt` metadata file is written here; that is handled by `filesystem.go`.

## Dependencies and Integration Points
Depends on Linux fscrypt ioctl constants, metadata structs, `util.Lookup`, and descriptor lengths from validation. Called by actions when encrypting directories and by filesystem support checks through `Mount.CheckSupport`.

## Risks
Ioctl behavior differs across kernel versions; the code includes fallbacks and error disambiguation but notes race potential when statting after `EINVAL`. `CheckSupport` deliberately calls set-policy with invalid data and must panic if the impossible success path occurs. Caller must ensure policy keys are provisioned before setting v2 policies as required by the kernel.

## Test Signals
`policy_test.go` covers setting policies on empty directories, failing on nonempty directories and files, rejecting bad descriptors, reading back v1 policy data, unencrypted directory errors, and v2 no-key behavior for non-root users when supported.
