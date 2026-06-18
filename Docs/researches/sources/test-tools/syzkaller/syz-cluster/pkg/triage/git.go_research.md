## sources/test-tools/syzkaller/syz-cluster/pkg/triage/git.go

`GitTreeOps` adapts syzkaller's `vcs.Git` to the `TreeOps` and base-diff operations needed by triage. `NewGitTreeOps` initializes a git checkout wrapper with environment inheritance, optional sandboxing, and a reset. `HeadCommit`, `Commit`, `ApplySeries`, and `BaseForDiff` expose tree branch lookup, commit lookup, patch application, and blob-based base detection.

The branch naming contract is tied to kernel-disk machinery: tree heads are addressed as `<tree.Name>/<tree.Branch>`, and non-hash commit references are resolved as `<treeName>/<branch>`. `ApplySeries` resets hard to the candidate commit, then applies each patch sequentially, returning the patch index on failure.

State mutation happens directly in the git worktree through reset and apply. Integration points are the triage workflow action, commit selector, and kernel repository PVC. Risks include destructive worktree mutation by design, sandbox test limitations noted in TODO, and dependence on branch naming conventions. Tests cover branch tag lookup and patch application success/failure in a temporary repo.
