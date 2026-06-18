<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.sh -->
# sources/test-tools/strace/tests/ipc.sh

Purpose: Shell harness for the `ipc` decoder test. It runs the compiled program and compares strace's `-eipc` output against program-generated expectations.

Important APIs/types/functions: Sources `init.sh`, calls `run_prog`, `run_strace -eipc`, writes expected output to `$EXP`, and validates with `match_grep`.

Control flow: The script runs the program once discarding stdout, then runs strace with IPC filtering and any passed arguments, redirects expected output, and greps the strace log against it.

State/persistence behavior: Uses the test framework's temporary `$LOG` and `$EXP` files. It creates no persistent repository state.

Dependencies: Depends on strace test harness shell functions and the compiled `ipc` test executable.

Integration points: Connects the C-side expected-output generator to the strace invocation layer for the legacy IPC multiplexer.

Risks: Harness variables must be initialized by `init.sh`; changing stdout/stderr handling in the C test or framework can break matching.

Test signals: Successful run exits 0 after `match_grep`; mismatches indicate decoder output drift.

Source read signal: complete file read for this research pass; file size 16 line(s), 282 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc.sh -->
