<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging.go -->
# sources/sync-backup/kopia/cli/command_policy_set_logging.go

Purpose: implements policy flags controlling snapshot logging detail for directory and entry events.

Important APIs/types/functions: `policyLoggingFlags`, `setLoggingPolicyFromFlags`, `applyPolicyLogDetailPtr`, `policy.LoggingPolicy`, and `policy.LogDetail`.

Control flow: setup registers six string flags for directory snapshotted/ignored and entry snapshotted/ignored/cache-hit/cache-miss detail levels. The setter applies each through `applyPolicyLogDetailPtr`; empty means unchanged, `inherit` clears the pointer, and numeric values must be within `LogDetailNone` through `LogDetailMax`.

State/persistence behavior: stores optional log-detail pointers in nested logging policy fields. Nil inherits the parent/default value.

Dependencies/integration: affects snapshot logging verbosity, policy show output, and inheritance definitions. Risks/test signals: accepted values are numeric rather than named levels; validation prevents out-of-range values and is covered by integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_logging.go -->
