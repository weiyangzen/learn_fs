# sources/sync-backup/rsync/testsuite/daemon-auth_test.py

Purpose: daemon authentication coverage for `auth users`, secrets files, password files, invalid credentials, and strict secrets-file modes.

Important APIs/types/functions: environment `RSYNC_PASSWORD`, `pwfile`, `push`, `write_daemon_conf`, `start_test_daemon`, `verify_dirs`, and `rsync_argv`.

Control flow: set a wrong fallback password to avoid interactive prompts, create an auth module with `tuser:secretpass`, push with correct password and verify data, push with wrong password and require rejection, try unauthenticated/invalid credentials with stdin closed and require rejection, then chmod secrets file world-readable and require strict-modes rejection.

State and persistence behavior: module backing directory is reset per push. Secrets file permissions are changed as part of the test.

Dependencies and integration points: daemon challenge/response auth, password-file handling, strict modes, and environment password fallback.

Risks and test signals: without fallback password the test could hang on `/dev/tty`. Failures indicate auth bypass, prompt behavior, or strict mode regression.
