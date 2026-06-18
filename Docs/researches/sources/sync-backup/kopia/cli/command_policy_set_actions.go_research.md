<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_actions.go -->
# sources/sync-backup/kopia/cli/command_policy_set_actions.go

Purpose: implements `policy set` flags for snapshot action commands that run before/after folder traversal or snapshot root processing.

Important APIs/types/functions: `policyActionFlags`, `setActionsFromFlags`, `setActionCommandFromFlags`, `quoteArguments`, `policy.ActionCommand`, and `maxScriptLength`.

Control flow: setup registers four action flags, timeout, mode, and script persistence. For each action, `"-"` means unchanged, empty string removes the action, and any other value creates a `policy.ActionCommand`. With `--persist-action-script`, the value is read as a file and embedded as repository-stored script text; otherwise it is parsed as a space-separated CSV command line with quote handling.

State/persistence behavior: stores action commands inside policy definitions, either as command/argument arrays or embedded script text. Embedded scripts are capped at 32,000 bytes.

Dependencies/integration: uses `encoding/csv` for shell-like argument splitting, `os.ReadFile` for script capture, and policy action execution semantics elsewhere. Risks/test signals: command parsing is not a full shell parser; storing script contents in repository state can preserve sensitive local script content.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_actions.go -->
