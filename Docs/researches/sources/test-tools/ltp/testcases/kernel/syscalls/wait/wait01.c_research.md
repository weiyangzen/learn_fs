<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait01.c

Purpose: verifies `wait(NULL)` fails with `ECHILD` when the calling process has no unwaited-for children.

Important APIs/types/functions: `verify_wait()` is a single `TST_EXP_FAIL2(wait(NULL), ECHILD)` assertion.

Control flow/state: no setup or child creation is performed; the process table state of interest is the absence of child processes.

Dependencies/integration: minimal LTP harness only. The test must run in isolation from stray children created by the harness.

Risks/test signals: any returned pid or errno other than `ECHILD` fails the basic wait contract. The test is intentionally narrow and low-flake.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/wait01.c -->
