<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/leaderkill.c -->
# sources/test-tools/strace/attic/test/leaderkill.c

Purpose: regression reproducer for thread group exit handling when a non-leader thread calls `exit`, causing group exit while the thread leader is still alive.

Important functions: `start0` sleeps then exits with status 42; `start1` pauses forever. `main` sleeps, forks, child creates both threads and pauses, parent waits for the process child and asserts exit status 42.

Control flow: delayed startup gives time to attach strace externally. The child thread group terminates through `exit(42)` in `start0`; parent validates propagated process exit status.

State and persistence: no persistent state; thread-group lifecycle is the observed state.

Dependencies and integration: pthreads, fork/wait, and strace attach/follow-fork behavior.

Risks: sleeps make timing-dependent attach windows. `exit` from a pthread has process-wide effects that are intentional but easy to misread. Test signals: running under `strace -f -p` should still allow the parent to print `OK`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/leaderkill.c -->
