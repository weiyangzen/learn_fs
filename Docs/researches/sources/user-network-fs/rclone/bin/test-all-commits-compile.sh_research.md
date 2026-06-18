# sources/user-network-fs/rclone/bin/test-all-commits-compile.sh

Purpose: branch hygiene helper that checks every commit on the current branch since `master` compiles with `go install ./...`. It is adapted for rebased feature branches.

Control flow rejects running on `master`, lists commits in reverse, checks out each commit, runs install, reports pass/fail, and returns to the original branch on failure or completion. State changes are destructive to the working tree checkout state and can disrupt uncommitted work. Dependencies are git and Go. Risks include no dirty-tree guard, branch name assumptions, stopping without nonzero explicit exit in one path, and potential generated/build-cache side effects. Test signal is compile success at each commit.
