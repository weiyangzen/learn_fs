# sources/sync-backup/git-lfs/lfs/scanner_git_test.go

Purpose: Provides git-level integration tests for `GitScanner` behavior across unpushed commits and historical pointer versions.

Important APIs/types/functions: Tests use `NewGitScanner`, `ScanUnpushed`, `ScanPreviousVersions`, `WrappedPointer`, test repository helpers, and `errors.Join` for callback aggregation.

Control flow: `TestScanUnpushed` creates branches and commits, pushes subsets to different remotes, and verifies pointer counts for all remotes, `origin`, and `upstream`. `TestScanPreviousVersions` creates a dated commit graph, scans old versions on `master` since a cutoff, sorts results by OID, and compares expected previous pointer states.

State and persistence behavior: Uses temporary Git repositories with real commit and remote state. No persistent repository mutation outside the test temp area; callbacks accumulate pointers in memory.

Dependencies and integration points: Integrates `lfs` scanner code with `config.New`, Git command execution, branch topology, remote refs, and pointer test utilities from `t/cmd/util`.

Risks and edge cases: Time-window tests depend on commit dates and branch ancestry. Remote-specific behavior must distinguish "pushed somewhere" from "pushed to a named remote".

Test signals: Strong integration signal for repository graph scanning. Does not inspect low-level channel error handling directly, but callback error aggregation would surface scanner failures.
