<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_test.go -->
# sources/sync-backup/kopia/internal/user/user_profile_test.go

- Purpose: Tests profile password setting and validation behavior.
- Important APIs/types/functions: `TestUserProfile`, `TestBadPasswordHashVersionWithSCrypt`, `TestBadPasswordHashVersionWithPbkdf2`, `TestUnsetPasswordHashVersion`, `TestNilUserProfile`, `TestInvalidPasswordHash`.
- Control flow: Tests set passwords under different versions, validate correct and incorrect passwords, mutate version fields to prove mismatch failure, verify version zero maps to scrypt, and validate nil/invalid-hash behavior.
- State and persistence: In-memory profiles only.
- Dependencies and integration points: Uses `internal/user` external test package and `testify/require`.
- Risks and edge cases: Does not measure timing resistance; only functional behavior.
- Test signals: Direct coverage for `user_profile.go` and `user_profile_pw_hash.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_profile_test.go -->
