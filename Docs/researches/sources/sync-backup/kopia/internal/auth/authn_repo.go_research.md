## sources/sync-backup/kopia/internal/auth/authn_repo.go

Purpose: repository-backed user authenticator that loads `user.Profile` manifests and validates passwords.

Important APIs/types/functions: `AuthenticateRepositoryUsers`, `repositoryUserAuthenticator`, `IsValid`, `Refresh`, and `defaultProfileRefreshFrequency`.

Control flow, state, and persistence: the authenticator caches profiles per repository with a mutex and refresh deadline. If the repository changes, it clears the profile map and forces reload. On refresh, it calls `user.LoadProfileMap`, logs errors without failing closed beyond current cache state, and validates `username` via `Profile.IsValidPassword`; nil map/profile behavior is intentionally safe.

Dependencies and integration points: depends on repository interfaces, `internal/user`, and `clock`. Used in server auth to support repository-managed users.

Risks and test signals: risks include stale user cache for up to the refresh frequency and continuing with old profiles after load errors. Tests cover valid/invalid users and password hash versions.
