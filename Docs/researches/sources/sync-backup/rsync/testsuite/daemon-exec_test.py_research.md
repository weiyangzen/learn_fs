# sources/sync-backup/rsync/testsuite/daemon-exec_test.py

Purpose: daemon hook coverage for `pre-xfer exec` and `post-xfer exec`, including environment variables and abort-on-pre-failure behavior.

Important APIs/types/functions: `script`, `wait_for`, `write_daemon_conf`, `start_test_daemon`, marker files, `rsync_argv`, and `test_fail`.

Control flow: create a source tree, marker directory, hook scripts that write `RSYNC_MODULE_NAME` and `RSYNC_EXIT_STATUS`, plus a failing pre-hook. Start daemon with `hook` and `failhook` modules. Push through `hook`, wait for marker files to contain `hook` and `0`, then push through `failhook` and require nonzero exit and no files written.

State and persistence behavior: marker files persist daemon-side hook environment observations; hook destination and fail destination show transfer side effects.

Dependencies and integration points: daemon exec hook invocation, environment population, asynchronous post-transfer timing, and module abort semantics.

Risks and test signals: post hook can race after client disconnect, hence polling. Failures mean hooks did not run, environment values changed, or failing pre-hook did not block writes.
