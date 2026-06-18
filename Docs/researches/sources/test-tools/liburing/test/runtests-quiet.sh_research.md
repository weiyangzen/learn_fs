# sources/test-tools/liburing/test/runtests-quiet.sh

Purpose: quiet wrapper around `runtests.sh` that suppresses output for passing runs and prints captured output only when the test run fails.

Important APIs/types/functions: `mktemp`, Bash arrays, stdout/stderr redirection, exit status propagation, `cat`, and `rm`.

Control flow: stores arguments in `TESTS`, creates a temporary result file, runs `./runtests.sh` with all output redirected there, captures `RET`, prints the file only for nonzero return, removes it, and exits with `RET`.

State/persistence behavior: creates one temporary file and deletes it before exit. It otherwise relies on `runtests.sh` for output directory and artifact management.

Dependencies/integration: assumes `runtests.sh` is executable in the current directory and `mktemp` is available. It preserves the main harness return semantics.

Risks/test signals: if interrupted before `rm`, the temp file may remain. Successful runs are silent, so timing/skip summaries from the underlying harness are hidden unless failure occurs.
