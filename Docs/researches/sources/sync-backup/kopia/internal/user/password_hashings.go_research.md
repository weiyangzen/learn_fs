<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings.go -->
# sources/sync-backup/kopia/internal/user/password_hashings.go

- Purpose: Maps stored password hash versions to crypto derivation algorithm identifiers.
- Important APIs/types/functions: `getPasswordHashAlgorithm`.
- Control flow: Switches version `0` and `1` to scrypt, version `2` to PBKDF2, and errors for unknown versions.
- State and persistence: Version numbers are persisted in user profiles and encoded hash payloads.
- Dependencies and integration points: Must match algorithm constants registered by `internal/crypto`.
- Risks and edge cases: Unsupported versions make password validation return errors for otherwise well-formed hashes.
- Test signals: `password_hashings_test.go` checks crypto constant alignment, dummy hash, and salt compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashings.go -->
