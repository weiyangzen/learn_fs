<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/lock_cmds_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/lock_cmds_test.py

Purpose: tests repository lock commands, especially `break-lock` and `with-lock` command execution under contention.

Important APIs: `cmd`, `CommandError`, `Path.as_uri`, subprocess `Popen`, `generate_archiver_tests`, and platform flags `is_haiku`/`is_win32`.

Control flow: `test_break_lock` simply creates a repository and runs `break-lock`. `test_with_lock` initializes a repo via `python3 -m borg`, runs one long-lived command under `borg with-lock`, then starts a second `with-lock` process with a short `--lock-wait`; the second command must not execute and must return the lock-timeout code. `test_with_lock_non_existent_command` verifies command launch failures are surfaced as `CommandError` exit codes.

State and persistence: uses `BORG_REPO` pointing at a file URI and keeps one subprocess blocked on stdin to hold the lock. Repository lock state is transient but critical.

Dependencies/integration: depends on importability of `borg` from subprocess Python, PATH/PYTHONPATH, repository locking, process exit codes, and forked execution. Risks include timing sensitivity in lock contention, platform skips, and binary/fork behavior. Test signals are stdout/stderr text, subprocess return codes, and command non-execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/lock_cmds_test.py -->
