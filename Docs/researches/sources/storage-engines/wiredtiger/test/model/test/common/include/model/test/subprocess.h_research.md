# sources/storage-engines/wiredtiger/test/model/test/common/include/model/test/subprocess.h

Purpose: declares a small subprocess harness for tests that need to isolate expected exits or crashes.

Important APIs and types: macros `in_subprocess` and `in_subprocess_abort`; class `subprocess_helper` with constructor/destructor, deleted copy/assign, `abort_if_child`, `exit_if_child`, `wait_if_parent`, `child`, and `parent`.

Control flow: the macros create a `subprocess_helper`, branch parent and child execution, wait in the parent, and exit or abort at the end of child scope. The helper constructor forks and installs monitoring; child code executes in the loop body; parent waits and then breaks.

State and persistence: stores child PID, sentinel path used to distinguish expected from unexpected child death, and previous SIGCHLD action. Persistent effects are temporary sentinel files under `/tmp`.

Dependencies and integration: includes POSIX process/signal headers and C `test_util.h`. Used by test code and indirectly by WT workload runner crash paths.

Risks: signal handling is process-global, so nested or concurrent subprocess helpers are sensitive. The macros rely on for-loop control flow and should be used carefully around returns/exceptions. Temporary sentinel cleanup must run in parent and child paths.

Test signals: tests should validate normal child exit, expected abort, unexpected child death failure, and restoration of prior SIGCHLD handler.
