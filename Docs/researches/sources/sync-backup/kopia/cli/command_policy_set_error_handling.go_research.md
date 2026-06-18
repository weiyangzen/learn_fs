<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_error_handling.go -->
# sources/sync-backup/kopia/cli/command_policy_set_error_handling.go

Purpose: implements `policy set` flags that control whether snapshot traversal ignores file read errors, directory read errors, and unknown filesystem entry types.

Important APIs/types/functions: `policyErrorFlags`, `setup`, `setErrorHandlingPolicyFromFlags`, `applyPolicyBoolPtr`, and `policy.ErrorHandlingPolicy`.

Control flow: setup registers three enum flags accepting `true`, `false`, or `inherit`. The setter applies each value to a `*policy.OptionalBool` field, wrapping parse errors with field-specific context.

State/persistence behavior: writes optional bool pointers into the policy. Nil means inherit/default; nonnil true/false overrides traversal behavior for the target.

Dependencies/integration: consumed by snapshot traversal and policy inheritance. Risks/test signals: the flag descriptions for directory and unknown-type errors have minor missing closing quotes, but enum validation prevents invalid values at CLI parse time; direct unit tests also exercise malformed values in the setter.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_error_handling.go -->
