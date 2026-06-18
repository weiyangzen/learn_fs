<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/00-hello_test.py -->
# sources/sync-backup/rsync/testsuite/00-hello_test.py

Purpose: foundational Python smoke test for rsync command availability, help output, local directory copying, local remote-shell behavior, and old-argument compatibility.

Important APIs/types/functions: imports `FROMDIR`, `TODIR`, `SRCDIR`, `RSYNC`, `RSYNC_PEER`, `checkit()`, `run_rsync()`, `test_fail()`, and later `rsync_argv()` from `rsyncfns`. Local helpers are `append_line()` and `copy_weird()`.

Control flow: set `RSYNC_RSH` to `support/lsh.sh`, verify `--version`, `--info=help`, and `--debug=help` exit successfully, create a source directory with shell-special characters in its name, append lines before successive transfers, and validate local copy plus pull/push transfers via `lh:` with and without `-s`. It then tests `--old-args` and `RSYNC_OLD_ARGS=1` by copying two files through a single remote argument string `one two` and confirming both files arrive.

State and persistence behavior: creates and mutates files under test `FROMDIR` and `TODIR`, changes current directory temporarily for old-args tests, and mutates a copy of the environment for the subprocess case.

Dependencies and integration points: depends on the Python rsync test harness, built rsync binaries, `support/lsh.sh`, and local-shell semantics for `lh:` hosts.

Risks: uses shell-sensitive path names and old-args behavior intentionally; failures may indicate quoting regressions rather than transfer engine problems. It imports `subprocess` mid-file and runs one command outside `run_rsync()` to inject environment.

Test signals: any nonzero help command fails the test; `checkit()` validates source/destination equality for transfer cases; explicit file-existence checks catch old-args and environment-variable compatibility regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/00-hello_test.py -->
