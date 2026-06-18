## sources/sync-backup/rsync/testsuite/partial_nowrite_test.py

Purpose: tests that `--partial --delay-updates` succeeds when destination temp-file permissions initially prevent writing, exercising chmod/retry behavior for partials.

Important APIs and control flow: creates a 1 MiB read-only source file, pre-populates `TODIR/.~tmp~/some_file`, and detects whether the run is root. On Linux root with `os.unshare` and `setpriv`, it tries to drop DAC override inside a private mount namespace so the permission-denied path is meaningful. Finally it runs `checkit(['-avv', '--partial', '--delay-updates', ...], FROMDIR, TODIR)`.

State and dependencies: local `FROMDIR`/`TODIR` are redefined under `TMPDIR`; it may mutate `rsyncfns.RSYNC` to prefix `setpriv`. It depends on Linux namespace/capability tooling when root.

Integration points: receiver temp update and partial retry logic.

Risks and test signals: root can bypass DAC, so the exact chmod-retry path may not be exercised on all root environments. Final tree equality is the acceptance signal.
