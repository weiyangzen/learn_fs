# sources/sync-backup/rsync/testsuite/batch-mode_test.py

Purpose: exercises rsync batch generation and replay modes locally and against daemon source/destination modules.

Important APIs/types/functions: `build_rsyncd_conf`, `hands_setup`, `run_rsync`, `checkit`, `verify_dirs`, `rsync_argv`, generated `BATCH` files and `BATCH.sh`, and helper `ignore23`.

Control flow: build expected `CHKDIR`, verify `--only-write-batch` does not create destination, replay with `--read-batch`, generate a local write-batch and replay it, start daemon, generate/replay daemon sender batch, run generated `BATCH.sh` twice, then push to daemon with `--write-batch` through `ignore23` and verify destination.

State and persistence behavior: batch side files live in `TMPDIR`; destination is repeatedly wiped and recreated. The expected tree excludes daemon global `foobar.baz`.

Dependencies and integration points: local batch mode, daemon sender/receiver batch mode, generated shell script replay, and harness directory verification.

Risks and test signals: daemon paths may return code 23 on otherwise acceptable transfers. Failures show bad batch replay, unwanted destination creation, or non-idempotent `BATCH.sh`.
