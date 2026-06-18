<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_remove.go -->
# sources/sync-backup/kopia/cli/command_policy_remove.go

Purpose: implements `kopia policy delete` with aliases `remove` and `rm`, removing defined policies for resolved policy targets.

Important APIs/types/functions: `commandPolicyDelete`, `policyTargetFlags`, `policyTargets`, `policy.RemovePolicy`, and the `--dry-run`/`-n` flag.

Control flow: setup registers target flags and dry-run, then uses a repository-writer action. `run` resolves all target arguments, logs each removal, skips mutation in dry-run mode, and otherwise calls `policy.RemovePolicy` per target.

State/persistence behavior: deletes policy definitions from the repository. Effective policy inheritance is not recomputed here; downstream policy lookups will fall back to parent/global definitions after removal.

Dependencies/integration: integrates target parsing and repository write transactions. Risks/test signals: removing multiple targets stops at the first remove error; dry-run still validates targets and logs intended changes, making it useful for target-resolution checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_remove.go -->
