## sources/sync-backup/kopia/internal/auth/authn_repo_test.go

Purpose: verifies repository-backed authentication against stored user profiles.

Important APIs/types/functions: `TestRepositoryAuthenticator`, `TestRepositoryAuthenticatorPasswordHashVersion`, and `verifyRepoAuthenticator`.

Control flow, state, and persistence: tests create a repository environment, write user manifests inside write sessions, set passwords with different hash versions, and call the authenticator against valid and invalid credential combinations.

Dependencies and integration points: exercises `repo.WriteSession`, `user.SetUserProfile`, password hashing, and `AuthenticateRepositoryUsers`.

Risks and test signals: confirms hash-version compatibility and negative credential behavior. It does not test profile refresh timing, repository switching, or load-error cache retention.
