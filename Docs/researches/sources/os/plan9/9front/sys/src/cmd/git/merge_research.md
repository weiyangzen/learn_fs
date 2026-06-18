# File Research: sources/os/plan9/9front/sys/src/cmd/git/merge

Simple merge driver script. It resolves `theirs`, `ours` (`HEAD`), and their LCA via `git/query ... @`. It refuses dirty working trees, fast-forwards by updating the current branch ref and running `git/revert .`, and otherwise records both parents in `.git/merge-parents`.

For real merges it computes changed paths from both sides with `git/query -c`, then invokes `merge1` per path against ours/base/theirs tree files exposed by `git/fs`. It leaves conflict/worktree state for the user to commit.
