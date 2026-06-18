<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export_test.go -->
# sources/sync-backup/kopia/cli/command_policy_export_test.go

Purpose: integration coverage for `policy export`, including default global policy output, target-specific export, path-to-source resolution, file output, overwrite behavior, pretty JSON, and error paths.

Important APIs/types/functions: `TestExportPolicy`, `testenv.NewCLITest`, `RunAndExpectSuccess`, `RunAndExpectFailure`, `testutil.MustParseJSONLines`, `snapshot.SourceInfo`, and `policy.Policy`.

Control flow: the test creates a filesystem repository with fixed user/host, exports the default global policy, sets a splitter policy on a temp directory, checks explicit full-source and local-path target export, exports all policies, writes to `--to-file`, verifies no overwrite by default, then verifies `--overwrite` and `--json-indent`.

State/persistence behavior: it mutates repository policy state through `policy set` and validates exported JSON against the expected in-memory policy map. It also creates and rereads a policy export file.

Dependencies/integration: depends on repository create/disconnect, policy set, policy export, filesystem temp paths, and JSON parsing. Risks/test signals: one assertion compares `expectedPolicy` against `policies5[id]` after overwrite instead of `policies7[id]`, but the surrounding length and parse checks still exercise overwrite output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_export_test.go -->
