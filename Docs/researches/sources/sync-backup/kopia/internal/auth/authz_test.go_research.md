## sources/sync-backup/kopia/internal/auth/authz_test.go

Purpose: validates no-access, legacy authorization, and default ACL authorization behavior.

Important APIs/types/functions: label fixtures, `TestNoAccess`, `TestLegacyAuthorizer`, `TestDefaultAuthorizer_NoACLs`, `TestDefaultAuthorizer_DefaultACLs`, `verifyLegacyAuthorizer`, and `verifyManifestAccessLevel`.

Control flow, state, and persistence: tests create repository environments, optionally add `auth.DefaultACLs` as ACL manifests, authorize selected users, and assert content and manifest access for global policy, host policy, user/path policy, and snapshots.

Dependencies and integration points: exercises `auth`, `acl.AddACL`, and repository testing.

Risks and test signals: strong signal that default ACLs intentionally preserve legacy visible behavior. Does not test custom ACL entries, invalid usernames, or cache invalidation after repository changes.
