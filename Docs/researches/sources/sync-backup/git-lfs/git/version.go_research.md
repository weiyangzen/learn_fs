# sources/sync-backup/git-lfs/git/version.go

Purpose: caches the installed Git version and compares Git version strings for feature gates.

Important APIs/types/functions: `Version`, `IsGitVersionAtLeast`, and `IsVersionAtLeast`.

Control flow: `Version` uses `sync.Once` around `subprocess.SimpleExec("git", "version")`. `IsGitVersionAtLeast` obtains the cached version and calls `IsVersionAtLeast`. The comparison regex extracts up to major/minor/patch numbers, scales them into a comparable integer, and ignores suffixes.

State/persistence behavior: process-global cached version and error. No file writes.

Dependencies/integration: used throughout this group for feature gates such as `git ls-files --sparse`, `git var GIT_ATTR_SYSTEM`, update-ref transactions, and worktree tests.

Risks/test signals: regex uses `.` unescaped for separators, so it is permissive beyond literal dots. Versions with components above 999 can collide with scale assumptions. Tests in `git_test.go` cover common comparisons.
