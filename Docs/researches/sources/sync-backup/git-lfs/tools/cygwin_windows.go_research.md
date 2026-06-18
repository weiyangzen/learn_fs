<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin_windows.go -->
# sources/sync-backup/git-lfs/tools/cygwin_windows.go

Purpose: Windows implementation that detects whether the process runs under Cygwin/MSYS-style environments.

Important APIs/types/functions: `cygwinSupport` enum, `Enabled`, package variable `cygwinState`, and `isCygwin`.

Control flow: `isCygwin` returns cached state when known. Otherwise it runs `uname` through the subprocess helper, reads output, marks enabled if it contains `CYGWIN` or `MSYS`, disabled otherwise, and returns the cached boolean. `Enabled` panics on unknown state.

State and persistence: caches detection in package global `cygwinState`; no disk state.

Dependencies and integration points: depends on `subprocess.ExecCommand` and translation package `tr`. Used by Windows path/terminal behavior elsewhere in tools.

Risks: global cache is not synchronized, so concurrent first calls can race under the Go race detector. Missing or failing `uname` disables Cygwin support. Panic in `Enabled` guards impossible unknown enum use.

Test signals: no direct tests in this subset; behavior is platform-specific and compile-tagged.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin_windows.go -->
