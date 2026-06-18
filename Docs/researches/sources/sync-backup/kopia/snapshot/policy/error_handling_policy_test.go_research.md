# sources/sync-backup/kopia/snapshot/policy/error_handling_policy_test.go

Purpose: verifies `ErrorHandlingPolicy.Merge` preserves optional boolean semantics.

Important APIs/types/functions: `TestErrorHandlingPolicyMerge` uses table-driven cases over `IgnoreFileErrors` and `IgnoreDirectoryErrors`, `NewOptionalBool`, and `reflect.DeepEqual`.

Control flow: each case constructs a starting policy, merges a source policy, and compares the result with the expected policy. Cases cover nil/no-op, source false, source true, destination already false/true, and changing only one field.

State and persistence behavior: no persistence; validates in-memory merge behavior that later determines persisted/effective policy values.

Dependencies/integration: depends on `snapshot.SourceInfo` only for definition argument. Tests do not assert definition-source fields.

Risks: `IgnoreUnknownTypes` is not covered in this test despite being merged by the source file; it relies on the same helper path.

Test signals: focused coverage for first-value-wins optional bool behavior, including explicit false.
