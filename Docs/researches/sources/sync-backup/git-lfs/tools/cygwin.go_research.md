<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin.go -->
# sources/sync-backup/git-lfs/tools/cygwin.go

Purpose: non-Windows implementation of Cygwin/MSYS detection.

Important APIs/types/functions: `isCygwin() bool`.

Control flow: build-tagged for `!windows`; always returns false.

State and persistence: none.

Dependencies and integration points: paired with `cygwin_windows.go`; callers can use `isCygwin` cross-platform without build-condition checks.

Risks: none beyond build tag correctness.

Test signals: no direct tests in this subset; platform build tags provide compile-time separation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/cygwin.go -->
