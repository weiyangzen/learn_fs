<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid09.c

Purpose: waitpid process-selection regression test that implements four direct cases for `WNOHANG`: running child returns 0, exited child returns pid, and no-child calls return `ECHILD` with and without `WNOHANG`.

Important APIs/types/functions: this file is built around `waitpid_common.h`, especially `waitpid_setup()`, `waitpid_test()`, `do_exit()`, `waitpid_ret_test()`, and `reap_children()`. Its local `do_child_1()` constructs the exact child/process-group/signal scenario for the case.

Control flow/state: the top-level harness forks a coordinator child; that child forks `MAXKIDS` children, stores pids in shared mmap, uses LTP checkpoints to hold or release them, then calls the common reaper. State includes child pid arrays, process groups, stop/continue state, and expected exit status 3 for helper children unless the file documents a direct special case.

Dependencies/integration: requires LTP checkpoints, shared anonymous mmap, and `.forks_child = 1`. The common cleanup kills any leftover child pids to avoid leaking blocked or stopped children.

Risks/test signals: these tests are race-prone without checkpoints; failures usually show as unexpected pid, unreaped child, wrong `ECHILD`, wrong exit status, or mishandled stopped child. Process-group cases are sensitive to `setpgid()` ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/waitpid/waitpid09.c -->
