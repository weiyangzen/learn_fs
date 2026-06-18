## sources/sync-backup/kopia/internal/acl/acl.go

Purpose: defines ACL entry schema, target matching rules, placeholders, and validation.

Important APIs/types/functions: `ContentManifestType`, `OwnUser`, `OwnHost`, `TargetRule`, `TargetRule.matches`, `Entry`, `Entry.Validate`, label validators, and allowed-label maps.

Control flow, state, and persistence: `Entry` is persisted as JSON in manifests while `ManifestID` is runtime-only. Validation requires `user@host`, a target `type`, labels allowed for that type, non-empty/one-of constraints, and a supported access level. Matching replaces `OWN_USER` and `OWN_HOST` placeholders with the authenticated username/hostname and then performs exact label matching.

Dependencies and integration points: integrates with manifest labels, snapshot/policy/user manifest types, and auth ACL evaluation.

Risks and test signals: risks include overly narrow label allowlists, placeholder substitution surprises, and the comment typo mentioning `OWN_VALUE` instead of `OWN_HOST`. ACL manager tests cover many validation errors and allowed target types.
