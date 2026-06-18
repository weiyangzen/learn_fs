## sources/test-tools/syzkaller/syz-cluster/pkg/triage/git_test.go

This file validates `GitTreeOps` against real temporary git repositories created by syzkaller test helpers. `TestGitTreeOpsHead` creates two commits and tags/refs that emulate kernel-disk naming, then confirms the correct tree/branch commit is resolved. `TestGitTreeOpsApply` confirms a good patch applies and a second non-applying patch produces an error after reset.

The embedded patch fixtures model realistic email-style git patches. These tests cover important integration behavior between syz-cluster triage and `pkg/vcs`, but they do not cover `BaseForDiff`, sandbox mode, or concurrent use of one checkout.
