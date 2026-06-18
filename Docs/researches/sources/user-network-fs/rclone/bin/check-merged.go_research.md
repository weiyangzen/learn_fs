# sources/user-network-fs/rclone/bin/check-merged.go

Purpose: standalone Go tool, excluded from normal builds, that helps determine whether local branches may already be merged into a target branch. It parses `git branch -v`, extracts branch name, revision, and log line, searches target branch history for the same commit subject, and when a match is found prints candidate evidence plus a diff-of-diffs between the branch revision and matched commit.

Important functions: `gitBranch` streams branch lines through regex `reLine`; `gitLogGrep` invokes `git log --grep`; `gitDiffDiff` shells through bash process substitution to compare `git show` output. State is read-only against git history, with stdout reporting. Dependencies include git and bash. Risks include commit-subject matching false positives/negatives, shelling with formatted revision arguments, and branch output format assumptions. Test signal is manual execution; no unit tests cover regex parsing.
