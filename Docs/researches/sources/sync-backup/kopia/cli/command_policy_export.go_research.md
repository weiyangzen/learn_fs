<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export.go -->
# sources/sync-backup/kopia/cli/command_policy_export.go

Purpose: implements `kopia policy export`, emitting defined policies as a JSON map keyed by `snapshot.SourceInfo.String()`. It supports exporting all policies, the global policy, or explicit targets, and can write either to stdout or a file.

Important APIs/types/functions: `commandPolicyExport`, `setup`, `run`, `getOutput`, `policyTargetFlags`, `policy.GetDefinedPolicy`, `policy.ListPolicies`, `json.Marshal`, `json.MarshalIndent`, and `exportFilePerms`. The hidden `--json-indent` flag changes formatting only.

Control flow: setup registers `--to-file`, `--overwrite`, target flags, and a repository-reader action. `run` opens output, resolves target-limited policies when `--global` or target arguments are present, otherwise lists all policies, marshals the map, writes a trailing newline, and closes file output through a joined defer path.

State/persistence behavior: repository state is read-only. File output is created with mode `0600` when exclusive creation is used; `--overwrite` uses `os.Create`, truncating an existing path. Passing `--overwrite` without `--to-file` is rejected.

Dependencies/integration: integrates policy target parsing, repository reader services, stdout abstraction, OS file creation, and policy JSON schemas. Risks/test signals: failures are mostly IO and target-resolution errors; JSON marshal is treated as impossible after typed map construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export.go -->
