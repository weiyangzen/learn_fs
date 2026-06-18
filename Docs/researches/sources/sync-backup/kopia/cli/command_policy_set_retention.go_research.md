<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_retention.go -->
# sources/sync-backup/kopia/cli/command_policy_set_retention.go

Purpose: implements retention-related `policy set` flags for snapshot keep counts and identical-snapshot suppression.

Important APIs/types/functions: `policyRetentionFlags`, `setRetentionPolicyFromFlags`, `applyOptionalInt`, `applyPolicyBoolPtr`, and `policy.RetentionPolicy`.

Control flow: setup registers keep counts for latest/hourly/daily/weekly/monthly/annual snapshots and `--ignore-identical-snapshots`. The setter iterates a table of retention count fields, applying optional integer parsing and inheritance clearing, then applies the optional bool.

State/persistence behavior: stores keep counts as `*policy.OptionalInt` pointers. Nil means inherit/default; explicit integer zero can be represented if provided and means a concrete keep count rather than inheritance.

Dependencies/integration: consumed by snapshot retention/maintenance logic and displayed by policy show. Risks/test signals: integer parsing has no domain-specific min/max in this layer; invalid retention semantics must be enforced by policy consumers or lower validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_retention.go -->
