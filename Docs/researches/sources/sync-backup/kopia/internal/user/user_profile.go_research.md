<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile.go -->
# sources/sync-backup/kopia/internal/user/user_profile.go

- Purpose: Defines user profile data and public password APIs.
- Important APIs/types/functions: `unsetDefaultHashVersion`, `ScryptHashVersion`, `Pbkdf2HashVersion`, `Profile`, `SetPassword`, `SetPasswordHash`, `IsValidPassword`.
- Control flow: `SetPassword` delegates to salted hash generation. `SetPasswordHash` decodes and validates an encoded hash before installing it. `IsValidPassword` validates against stored hash, or computes against a dummy hash for nil profiles to reduce account-existence timing leakage.
- State and persistence: `Profile` fields are JSON-serializable repository manifest content; `ManifestID` is in-memory only.
- Dependencies and integration points: Integrates manifest IDs and password hashing helpers.
- Risks and edge cases: Nil-profile dummy hashing assumes dummy hash length/version remain valid; invalid stored hash length returns false without error.
- Test signals: `user_profile_test.go` covers valid/invalid passwords, algorithm mismatch, unset version, nil profile, and invalid hash bytes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile.go -->
