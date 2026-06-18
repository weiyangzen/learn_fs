# sources/security-integrity/fscrypt/keyring/fs_keyring.go

## Purpose
`fs_keyring.go` implements the modern fscrypt filesystem-keyring ioctl path for adding, removing, and querying encryption keys on a mounted filesystem.

## Important APIs, Types, and Functions
Public support detection is `IsFsKeyringSupported`. Internal core functions are `fsAddEncryptionKey`, `fsRemoveEncryptionKey`, `fsGetEncryptionKeyStatus`, `buildKeySpecifier`, `dropPrivsIfNeeded`, `restorePrivs`, and `validateKeyDescriptor`.

## Control Flow
Support detection opens the mount path and probes `FS_IOC_ADD_ENCRYPTION_KEY` with a null argument, treating `ENOTTY` as unsupported and `EFAULT` as supported. Add builds a locked `FscryptAddKeyArg` plus raw key payload, fills the key specifier from a hex descriptor, optionally drops UIDs for v2 user claims, invokes the add ioctl, restores privileges, then validates the returned v2 descriptor. Remove chooses either single-user or all-users ioctl, interprets removal status flags, and maps kernel states to package errors. Status maps kernel status and flags to `KeyStatus`.

## State and Persistence
State is in the kernel keyring and fscrypt key claims, not on disk. Support detection is cached globally in `fsKeyringSupported`/`fsKeyringSupportedKnown`. UID changes are process-wide through the `security` package and are restored after each ioctl.

## Dependencies and Integration Points
Depends on `crypto.Key` for locked ioctl buffers, `filesystem.Mount`, `security.SetUids/GetUids`, Linux fscrypt ioctl structs/constants from `unix`, and cgo `memcpy`. It is selected by `keyring.go` for v2 policy descriptors and optionally for v1 descriptors.

## Risks
Privilege changes are process-wide and risky in multithreaded Go programs, though the code restores saved IDs. Failure to restore privileges is not propagated if ignored after ioctl. Support is cached globally after the first mount probe, assuming kernel-wide support. Incorrect v2 descriptors trigger best-effort cleanup.

## Test Signals
`keyring_test.go` covers v1 filesystem keyring when root and supported, v2 add/remove/status, cross-user removal behavior, multiple-user claims, wrong descriptors, bad mounts, and all-user removal.
