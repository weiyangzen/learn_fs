<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_files.go -->
# sources/sync-backup/kopia/cli/command_policy_set_files.go

Purpose: implements file selection policy flags for ignores, dot-ignore files, maximum file size, filesystem-boundary traversal, and cache-directory ignores.

Important APIs/types/functions: `policyFilesFlags`, `setFilesPolicyFromFlags`, `applyPolicyNumber64`, `applyPolicyStringList`, `applyPolicyBoolPtr`, and `policy.FilesPolicy`.

Control flow: setup registers add/remove/clear variants for ignore rules and dot-ignore files, a `--max-file-size` string, `--one-file-system`, and `--ignore-cache-dirs`. The setter parses the scalar max size, updates list fields with sorted unique values, then applies optional booleans.

State/persistence behavior: stores ignore lists and traversal limits in policy definitions. `clear-*` sets lists to nil; scalar max size of zero means inherited/default.

Dependencies/integration: consumed by snapshot source traversal and ignore-rule evaluation. Risks/test signals: max file size uses a raw integer parser, unlike some user-facing size displays; list operations increment change count even when adding an existing value or removing a missing one.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_files.go -->
