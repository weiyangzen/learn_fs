# sources/sync-backup/kopia/snapshot/policy/error_handling_policy.go

Purpose: defines optional error-handling behavior for snapshot traversal.

Important APIs/types/functions: `ErrorHandlingPolicy` has optional booleans for file errors, directory errors, and unknown entry types. `ErrorHandlingPolicyDefinition` records definition sources. `Merge` fills unset optional values from a source policy.

Control flow: merge delegates to `mergeOptionalBool`, preserving the first non-nil value in most-specific-to-general policy order.

State and persistence behavior: optional booleans persist as JSON only when set, allowing explicit false to differ from unspecified.

Dependencies/integration: used by policy merging and snapshot upload error handling. Depends on `OptionalBool` and `snapshot.SourceInfo`.

Risks: nil vs false is semantically important; code consuming these fields must use `OrDefault` rather than direct boolean casts.

Test signals: `error_handling_policy_test.go` specifically verifies merge semantics for nil, false, true, and partial values.
