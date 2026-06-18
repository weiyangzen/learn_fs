# sources/sync-backup/kopia/snapshot/policy/policy_merge.go

Purpose: merges ordered policy hierarchy into one effective policy and tracks which source supplied each field.

Important APIs/types/functions: `MergePolicies` and merge helpers: `mergeOptionalBool`, `mergeOptionalInt`, `mergeOptionalInt64`, `mergeStringsReplace`, `mergeStrings`, `mergeString`, `mergeCompressionName`, `mergeInt64`, `mergeBool`, `mergeStringList`, `mergeLogLevel`, and `mergeActionCommand`.

Control flow: `MergePolicies` initializes labels for the requested source, applies supplied policies in most-specific-to-general order, stops early if a policy has `NoParent`, then merges default policies for every subpolicy category. After inherited merging, it copies non-inheritable folder actions from the most-specific policy. Helpers generally implement first-value-wins semantics and record `snapshot.SourceInfo` in definition structs.

State and persistence behavior: produces an in-memory effective policy and definition object; it does not write manifests. Effective fields ultimately drive snapshot behavior and may be displayed to users.

Dependencies/integration: combines all subpolicy merge methods, default policy globals from other files, compression names, and snapshot source info.

Risks: helper semantics differ: some list helpers replace only if empty, while `mergeStrings` unions and supports a no-parent stop flag. This makes subpolicy behavior non-uniform and easy to misuse. `NoParent` stops before default policy merge, meaning defaults are skipped when a user policy sets `NoParent`.

Test signals: policy manager tests verify effective retention merges and definitions; error-handling/logging/OS tests cover specific helper paths indirectly. More direct tests would help for list/no-parent semantics.
