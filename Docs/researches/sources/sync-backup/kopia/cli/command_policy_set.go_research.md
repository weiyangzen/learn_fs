<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set.go -->
# sources/sync-backup/kopia/cli/command_policy_set.go

Purpose: central implementation of `kopia policy set`, coordinating many flag groups that mutate a `policy.Policy` definition for one or more targets.

Important APIs/types/functions: `commandPolicySet`, `setPolicyFromFlags`, helper functions `applyPolicyStringList`, `applyOptionalInt`, `applyOptionalInt64MiB`, `applyPolicyNumber64`, `applyPolicyBoolPtr`, `supportedCompressionAlgorithms`, `policy.GetDefinedPolicy`, and `policy.SetPolicy`.

Control flow: setup registers target flags, `--inherit`, and all sub-policy flag groups. `run` resolves targets, loads the existing defined policy or starts a new one for missing targets, applies all flag groups in a fixed order, rejects invocations with zero changes, and persists the result.

State/persistence behavior: writes complete defined policy objects. Optional pointer fields use nil to mean inherited/default, while scalar numeric fields use zero for inherited/default. String-list helpers build sorted unique lists from add/remove/clear operations.

Dependencies/integration: depends on compression registry, policy inheritance conventions, repository writer sessions, and all sibling flag structs. Risks/test signals: some helpers mutate earlier fields before returning an error from a later field, so callers must rely on the outer command not persisting when an error is returned.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set.go -->
