## sources/sync-backup/kopia/internal/acl/acl_manager.go

Purpose: loads, filters, evaluates, and writes ACL manifest entries.

Important APIs/types/functions: `EntriesForUser`, `EffectivePermissions`, `LoadEntries`, `AddACL`, `matchOrWildcard`, and `userMatches`.

Control flow, state, and persistence: ACLs are stored as manifests labeled `type=acl`. `LoadEntries` lists manifests, reuses entries from a caller-provided cache by manifest ID, loads misses, and attaches IDs. `EffectivePermissions` scans matching user and target rules, returning the highest access level. `AddACL` validates, loads existing ACLs, optionally replaces same user+target entries, and writes the new manifest.

Dependencies and integration points: depends on repository manifest APIs and `Entry.Validate`. Auth uses this as the ACL source of truth.

Risks and test signals: risks include cache staleness if a manifest changes under the same ID, wildcard-only user matching, and overwrite semantics that delete old entries before writing new ones. Tests cover effective permissions, cache reuse loading, validation, and add behavior.
