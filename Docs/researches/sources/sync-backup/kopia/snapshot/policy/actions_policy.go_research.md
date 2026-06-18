# sources/sync-backup/kopia/snapshot/policy/actions_policy.go

Purpose: defines snapshot action-command policy fields and inheritance behavior.

Important APIs/types/functions: `ActionsPolicy` contains non-inherited `BeforeFolder`/`AfterFolder` commands and inherited `BeforeSnapshotRoot`/`AfterSnapshotRoot` commands. `ActionCommand` stores command path, args, inline script, timeout, and mode. `ActionsPolicyDefinition` tracks definition sources for inherited root commands. Methods `Merge` and `MergeNonInheritable` apply inheritance.

Control flow: `Merge` fills unset snapshot-root commands from a source policy and records definition source. `MergeNonInheritable` copies folder-level commands from the most specific policy after inherited merge is complete.

State and persistence behavior: policy fields persist in policy manifests as JSON. Definition source info is computed, not persisted as part of the policy.

Dependencies/integration: used by `MergePolicies` and snapshot upload action execution code elsewhere. Depends on `snapshot.SourceInfo` for definition tracking.

Risks: folder-level commands are intentionally non-inheritable; treating them as inherited could execute commands in unintended directories. `Mode` is a free string, so validation likely lives elsewhere or may be lax.

Test signals: policy merge tests cover inherited policy mechanics broadly; action-specific execution is outside this file.
