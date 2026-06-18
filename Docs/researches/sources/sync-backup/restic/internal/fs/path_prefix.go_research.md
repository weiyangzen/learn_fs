# sources/sync-backup/restic/internal/fs/path_prefix.go

Purpose: Determines whether one path is equal to or inside another path.

Important APIs: `HasPathPrefix`.

Control flow and state: Compares volume names and absolute/relative status, cleans paths, returns true for equality, then walks parent directories of `p` until root looking for `base`.

Dependencies and integration: Used by VSS mount-point snapshot mapping to detect whether a requested path lies under a mount point.

Risks: Matching is case-sensitive by design, while Windows callers lower-case paths before use where needed. Relative path semantics can make `"."` a prefix of cleaned relative paths.

Test signals: `path_prefix_test.go` covers equality, root behavior, sibling false positives, case sensitivity, absolute/relative mismatch, and Windows drive normalization.
