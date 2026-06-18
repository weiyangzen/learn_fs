# sources/sync-backup/borg/src/borg/testsuite/helpers/process_test.py

Purpose: tests subprocess command parsing and error handling wrapper behavior.

Important APIs and control flow: `TestPopenWithErrorHandling` runs `test 1` when available, expects `None` for a definitely missing command, expects `None` for bad shell-like command syntax and empty strings, and asserts `shell=True` is rejected.

State and persistence: launches a short process only for the simple case. No persistent state.

Dependencies and integration points: depends on `shutil.which`, pytest skips/parametrization, and `helpers.process.popen_with_error_handling`. It protects helpers that run external commands such as passphrase commands or remote transports.

Risks: availability of the POSIX `test` command is platform-dependent. The missing-command name must remain absent from PATH for the skip logic to be meaningful.

Test signals: process exit code zero, `None` on parse/not-found failure, and assertion on forbidden shell mode.
