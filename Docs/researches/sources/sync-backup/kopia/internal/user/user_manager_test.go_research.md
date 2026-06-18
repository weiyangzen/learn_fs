<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager_test.go -->
# sources/sync-backup/kopia/internal/user/user_manager_test.go

- Purpose: Tests repository-backed user profile lifecycle and username validation.
- Important APIs/types/functions: `TestUserManager`, `TestGetNewProfile`, `TestValidateUsername_Valid`, `TestValidateUsername_Invalid`.
- Control flow: Uses a repotesting environment, sets profiles, reads updated hashes, deletes users, checks not-found errors, creates passworded new profiles, and table-tests valid/invalid username strings.
- State and persistence: Uses repository manifests in a test repository.
- Dependencies and integration points: Integrates `repotesting`, `internal/user`, and `testify/require`.
- Risks and edge cases: Does not test `LoadProfileMap` cache reuse or concurrent writers.
- Test signals: Direct coverage for `user_manager.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager_test.go -->
