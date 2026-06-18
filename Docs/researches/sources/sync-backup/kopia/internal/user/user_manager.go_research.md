<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager.go -->
# sources/sync-backup/kopia/internal/user/user_manager.go

- Purpose: Manages user profile manifests in the repository.
- Important APIs/types/functions: `ManifestType`, `UsernameAtHostnameLabel`, `ErrUserNotFound`, `ErrUserAlreadyExists`, `LoadProfileMap`, `ListUserProfiles`, `GetUserProfile`, `GetNewProfile`, `ValidateUsername`, `SetUserProfile`, `DeleteUserProfile`.
- Control flow: Functions find manifests by type/name labels, dedupe latest entries, reuse cached profiles by manifest ID, load profiles, validate lowercase `user@hostname`, replace manifests for writes, and delete all matching manifests.
- State and persistence: User profiles persist as repository manifests labeled `type=user` and `username=<username@hostname>`.
- Dependencies and integration points: Integrates `repo`, `manifest`, `maps`, `slices`, and username validation used by auth/user management flows.
- Risks and edge cases: Username validation is restrictive and lowercase-only; cache reuse depends on stable manifest IDs.
- Test signals: `user_manager_test.go` covers create/update/delete, missing user, duplicate new profile, and username validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/user_manager.go -->
