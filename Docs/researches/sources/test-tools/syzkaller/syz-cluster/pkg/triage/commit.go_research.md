## sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit.go

This file contains commit-selection logic for choosing a base kernel commit on which a patch series should be tested. It defines `TreeOps`, `CommitSelector`, `SelectResult`, public `Select`, and base-commit helpers `FromBaseCommits` and `bestCommit`.

`Select` queries the tree head, rejects series more than seven days behind head, optionally tries a recent last successful build first, then tries current head. Each candidate is accepted only if `TreeOps.ApplySeries` applies all patch bodies. Failure reasons distinguish age from non-applicability. `FromBaseCommits` ranks blob-detected base commits by trees selected from series Cc/tags first, then all configured trees; `bestCommit` prefers earlier tree order and exact branch matches.

Dependencies are abstracted through `TreeOps`, `debugtracer`, `vcs`, and syz-cluster API types. Integration points are `workflow/triage/main.go` and `GitTreeOps`. Risks include the fixed seven-day cutoff, no support yet for intentionally stale experimental sessions, and branch ranking depending on configured tree order. Unit tests cover freshness, last-build preference, non-applying patches, and base-commit/tree ranking.
