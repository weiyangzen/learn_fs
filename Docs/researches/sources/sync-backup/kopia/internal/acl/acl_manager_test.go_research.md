## sources/sync-backup/kopia/internal/acl/acl_manager_test.go

Purpose: tests ACL matching, effective permission computation, repository load/add, and validation errors.

Important APIs/types/functions: `TestEffectivePermissions`, `TestLoadEntries`, and `TestACLEntryValidation`.

Control flow, state, and persistence: tests create in-memory repository environments, add ACL manifests, reload with cached prior entries, and evaluate label maps for users/hosts. Validation cases assert exact error messages for invalid target types, labels, policy types, users, missing type labels, and invalid access.

Dependencies and integration points: exercises `acl` package against real repository manifest operations through `repotesting`.

Risks and test signals: strong signal for intended ACL semantics, including highest-access-wins and placeholder matching. Does not test delete failure recovery in `AddACL` or concurrent ACL writes.
