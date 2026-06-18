<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password_test.go -->
# sources/sync-backup/kopia/internal/user/hash_password_test.go

- Purpose: Tests encoded password hash creation, decode, profile validation, and `passwordHash.validate`.
- Important APIs/types/functions: `TestHashPassword_encoding`, `TestPasswordHashValidate`.
- Control flow: Generates a random petname password, hashes/decodes it, constructs a profile, validates the password, then table-tests invalid versions and lengths.
- State and persistence: In-memory hash payloads only.
- Dependencies and integration points: Uses `golang-petname` and `testify/require`.
- Risks and edge cases: Random password content is non-deterministic but not security-sensitive.
- Test signals: Direct coverage for `hash_password.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/hash_password_test.go -->
