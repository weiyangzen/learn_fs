## sources/sync-backup/kopia/internal/auth/authz.go

Purpose: authorization interfaces plus legacy pre-ACL authorization rules.

Important APIs/types/functions: `Authorizer`, `AuthorizationInfo`, access-level aliases, `NoAccess`, `LegacyAuthorizer`, `legacyAuthorizationInfo`, and `ManifestAccessLevel`.

Control flow, state, and persistence: legacy authorization grants full content access, read access to global policy, read access to own host policy, and full access to manifests whose username/hostname labels match the authenticated `username@hostname`. No state is persisted in this file.

Dependencies and integration points: consumes manifest, snapshot, and policy labels; provides fallback behavior for `DefaultAuthorizer` when no ACLs exist.

Risks and test signals: risks include label-map omissions causing empty-string comparisons and full content access in legacy mode. Authz tests cover no-access and legacy/default behavior across policy/snapshot label combinations.
