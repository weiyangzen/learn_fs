<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashing_version.go -->
# sources/sync-backup/kopia/internal/user/password_hashing_version.go

- Purpose: Declares the default password hashing scheme for new user password hashes.
- Important APIs/types/functions: `defaultPasswordHashVersion`.
- Control flow: Declaration-only file selecting `ScryptHashVersion`.
- State and persistence: Compile-time constant affects newly generated/stored hashes.
- Dependencies and integration points: Used by `HashPassword`, `GetNewProfile`, and profile password setting.
- Risks and edge cases: Changing this constant affects future hashes but old hashes rely on stored versions.
- Test signals: User profile/hash tests exercise default behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/user/password_hashing_version.go -->
