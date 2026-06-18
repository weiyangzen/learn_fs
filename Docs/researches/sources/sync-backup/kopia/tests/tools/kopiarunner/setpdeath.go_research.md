<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath.go -->
# sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath.go

This non-Linux file provides a no-op `setpdeath` implementation for async Kopia commands. It returns the command unchanged.

The integration point is `Runner.RunAsync`, which calls `setpdeath` before starting server processes. On non-Linux systems there is no parent-death signal configuration, so child server cleanup relies on explicit test cleanup.

Risks are platform behavior differences: orphaned async server processes are more likely if tests crash on non-Linux. Linux-specific behavior is implemented separately. Test signals are indirect through server-mode robustness tests on each platform.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/tools/kopiarunner/setpdeath.go -->
