<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import_test.go -->
# sources/sync-backup/kopia/cli/command_policy_import_test.go

Purpose: end-to-end coverage for importing policy JSON, target-limited imports, unknown-field handling, deletions, global-target equivalence, and invalid input failures.

Important APIs/types/functions: `TestImportPolicy`, `assertPoliciesEqual`, `json.Marshal`, `os.WriteFile`, `testutil.MustParseJSONLines`, `policy.DefaultPolicy`, and `snapshot.SourceInfo`.

Control flow: the test creates a repository, deep-copies the default global policy, writes JSON policy files, imports changes, adds local policies, restricts imports to `(global)` or a specific source, validates that deleted fields clear policy values, adds a second target, tests unknown fields with and without `--allow-unknown-fields`, and exercises `--delete-other-policies`.

State/persistence behavior: repository policies are repeatedly replaced and removed, and expected state is always validated through `policy export`, not direct internals. File state is a generated `policy.json`.

Dependencies/integration: depends on `policy export` for verification and on stable JSON names for `policy.Policy`. Risks/test signals: because it is integration-style, failures can originate in export, source parsing, or policy set serialization as well as import itself.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_import_test.go -->
