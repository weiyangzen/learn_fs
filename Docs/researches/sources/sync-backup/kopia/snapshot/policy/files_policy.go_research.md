# sources/sync-backup/kopia/snapshot/policy/files_policy.go

Purpose: defines file-selection policy for snapshot traversal.

Important APIs/types/functions: `FilesPolicy` includes ignore rules, dot-ignore filenames, no-parent flags, cache-directory ignoring, max file size, and one-file-system behavior. `FilesPolicyDefinition` tracks source locations. `Merge` applies inherited values.

Control flow: merge copies ignore rules only when target is empty, merges no-parent booleans, replaces dot-ignore files when target is empty, merges optional booleans, and fills max file size if unset.

State and persistence behavior: fields persist as JSON in policy manifests. Optional booleans distinguish unset from explicit false.

Dependencies/integration: consumed by snapshot upload/walk code and policy merge. Depends on `OptionalBool` and `snapshot.SourceInfo`.

Risks: `NoParentIgnoreRules` is merged as a boolean but does not appear to stop `IgnoreRules` merging in this file; contrast with compression `mergeStrings` no-parent behavior. The distinction between append/replace semantics for ignore rules and dot-ignore files should be preserved.

Test signals: policy manager tests exercise inherited policies generally; file-policy-specific behavior is not directly tested in this subset.
