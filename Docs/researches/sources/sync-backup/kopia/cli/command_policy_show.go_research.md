<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_show.go -->
# sources/sync-backup/kopia/cli/command_policy_show.go

Purpose: implements `kopia policy show`/`get`, displaying effective policy for one or more targets as JSON or a human-aligned text table with definition/inheritance annotations.

Important APIs/types/functions: `commandPolicyShow`, `policy.GetEffectivePolicy`, `printPolicy`, `policyTableRow`, `alignedPolicyTableRows`, `definitionPointToString`, and append helpers for retention, files, error handling, scheduling, upload, compression, metadata compression, splitter, actions, OS snapshots, and logging.

Control flow: setup registers target and JSON flags. `run` resolves targets, loads effective policy plus definition provenance, and emits JSON or formatted text. Text formatting builds rows by policy category, computes alignment widths, and appends provenance such as `(defined for this target)` or `inherited from ...`.

State/persistence behavior: read-only. It displays effective values after inheritance resolution, not merely defined local policy fields.

Dependencies/integration: depends on policy definition tracking, source-info rendering, unit formatting, and action command formatting. Risks/test signals: output is user-facing and heavily asserted by policy tests; changes to row labels, defaults, or alignment may break tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_show.go -->
