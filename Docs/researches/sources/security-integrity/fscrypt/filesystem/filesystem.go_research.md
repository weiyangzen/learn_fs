# sources/security-integrity/fscrypt/filesystem/filesystem.go

## Purpose
`filesystem.go` implements fscrypt metadata storage for a mounted filesystem. It creates and validates the `.fscrypt` directory tree, reads and writes policy/protector protobuf files, links protectors across filesystems, filters metadata by trusted owners, and protects metadata reads from malicious filesystem objects.

## Important APIs, Types, and Functions
Key types are `Mount`, `SetupMode`, `ErrAlreadySetup`, `ErrCorruptMetadata`, `ErrFollowLink`, `ErrInsecurePermissions`, `ErrNoCreatePermission`, `ErrNotSetup`, `ErrPolicyNotFound`, and `ErrProtectorNotFound`. Public methods include `BaseDir`, `ProtectorDir`, `PolicyDir`, `PolicyPath`, `CheckSupport`, `CheckSetup`, `GetSetupMode`, `Setup`, `RemoveAllMetadata`, `AddProtector`, `AddLinkedProtector`, `GetRegularProtector`, `GetProtector`, `RemoveProtector`, `ListProtectors`, `AddPolicy`, `GetPolicy`, `RemovePolicy`, and `ListPolicies`.

## Control Flow
Setup first checks if metadata already exists, rejects unsupported filesystem types, builds a temporary mount directory, creates `.fscrypt/policies` and `.fscrypt/protectors` with the selected permissions, then atomically renames into place. Metadata writes validate protobuf objects, marshal with `proto.Marshal`, preserve existing owner/mode when possible, write to a synced temporary file, rename over the destination, and sync the parent directory. Reads use `readMetadataFileSafe`, unmarshal, then call `CheckValidity`.

## State and Persistence
Persistent state lives under `<mount>/.fscrypt`, or under a symlink target if `.fscrypt` was intentionally pre-created as a symlink. Policy and protector files are protobuf-encoded and normally mode `0600`. Linked protectors are small `.link` files containing `UUID=` and/or `PATH=` records pointing to another mount. `RemoveAllMetadata` atomically renames the metadata directory away and deletes it via deferred cleanup.

## Dependencies and Integration Points
The file integrates with `metadata` protobuf validation, `mountpoint.go` link resolution via `makeLink` and `getMountFromLink`, `path.go` stat helpers, `util` user/ownership helpers, `unix` for umask and open flags, and `actions` callers that use metadata to unlock/provision policies. It is the persistence layer for protectors and policies consumed by the CLI and PAM module.

## Risks
Metadata security depends on ownership checks and rejecting symlinks/FIFOs/oversized files. The non-atomic overwrite fallback can corrupt an existing file if the write fails, though it is only used when directory creation is denied but file write is possible. `CheckSetup` intentionally allows `.fscrypt` itself to be a symlink, which supports read-only root filesystems but increases reliance on owner and subdirectory checks. `SortDescriptorsByLastMtime` is global mutable state for tests.

## Test Signals
`filesystem_test.go` covers setup/removal, absolute and relative `.fscrypt` symlinks, setup modes, insecure permissions, invalid metadata rejection, policy/protector round trips, spoofed login protector ownership, metadata file modes, linked protectors, and safe metadata-file reads rejecting symlinks, FIFOs, nonexistent files, and oversized files.
