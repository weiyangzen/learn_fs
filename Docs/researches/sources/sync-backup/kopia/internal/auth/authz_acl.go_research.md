## sources/sync-backup/kopia/internal/auth/authz_acl.go

Purpose: ACL-backed authorizer with defaults and repository ACL caching.

Important APIs/types/functions: `ContentRule`, `DefaultACLs`, `DefaultAuthorizer`, `aclCache`, `aclEntriesAuthorizer`, `Authorize`, and `Refresh`.

Control flow, state, and persistence: `Authorize` parses `username@hostname`, refreshes cached ACL entries periodically via `acl.LoadEntries`, falls back to legacy rules when no ACLs exist, and returns an `AuthorizationInfo` that evaluates content and manifest access through ACL rules filtered for the user. ACL entries themselves persist as repository manifests.

Dependencies and integration points: integrates `acl` package, repository manifests, user/policy/snapshot label names, and `clock`.

Risks and test signals: the repository-change cache reset condition appears inverted (`if rep == ac.lastRep`) despite the comment saying reset when the server switches repositories; this may force unnecessary reloads for same repo and fail to clear cache for a new repo. Tests cover no-ACL fallback and default ACL equivalence, but not repository switching or refresh timing.
