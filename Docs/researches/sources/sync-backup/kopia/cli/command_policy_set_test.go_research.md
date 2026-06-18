<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_test.go -->
# sources/sync-backup/kopia/cli/command_policy_set_test.go

Purpose: focused unit tests for setter helpers in `policy set`, especially error-handling optional bools and scheduling policy transitions.

Important APIs/types/functions: `TestSetErrorHandlingPolicyFromFlags`, `TestSetSchedulingPolicyFromFlags`, `policyErrorFlags`, `policySchedulingFlags`, `policy.ErrorHandlingPolicy`, `policy.SchedulingPolicy`, and `testlogging.Context`.

Control flow: the error-handling table covers no-op, malformed input, partial mutation before error, inherit clearing, true/false overrides, and mixed values. The scheduling table covers no-op, manual mode, interval, times of day, invalid manual/schedule combinations, clearing existing schedules when manual is set, resetting manual when schedules are set, cron parsing, invalid cron validation, inherited cron, and `RunMissed`.

State/persistence behavior: tests mutate in-memory policy structs and count changes; no repository is opened. The tests explicitly document that setters may partially mutate before returning errors.

Dependencies/integration: validates local helper semantics independent of kingpin enum parsing and repository writes. Risks/test signals: one error-handling test ignores returned errors/change-count assertions, so its main signal is final struct shape rather than exact error propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_policy_set_test.go -->
