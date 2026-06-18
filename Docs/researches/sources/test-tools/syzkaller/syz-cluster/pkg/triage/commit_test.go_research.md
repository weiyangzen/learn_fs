## sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit_test.go

This test file validates commit-selection heuristics with deterministic fake tree operations. `TestCommitSelector` covers fresh series, fresh/stale last build preference, slightly old versus too-old series, fallback from failed last-build application to head, and no-applicable-commit outcomes.

`TestFromBaseCommits` builds ordered tree/base-commit fixtures and verifies selection by exact branch, higher-priority tree among Cc-matching trees, and fallback to any tree when Cc-selected trees do not appear. Helpers include a date parser, shared `testTree`, and `testGitOps` implementing `HeadCommit` and `ApplySeries` through maps.

The tests are strong signals for branch ranking and age/apply behavior but do not exercise real git, tracer output, nil head edge cases beyond returning nil errors, or concurrent repository mutation. Real git behavior is separately tested in `git_test.go`.
