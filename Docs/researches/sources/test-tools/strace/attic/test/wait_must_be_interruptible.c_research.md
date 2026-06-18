<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/wait_must_be_interruptible.c -->
# sources/test-tools/strace/attic/test/wait_must_be_interruptible.c

Purpose: regression reproducer for ensuring a traced `wait` remains interruptible by signals under `strace -f`.

Important functions: `handler` writes the parent signal message. `test` installs SIGALRM handler, forks a child that signals parent between two writes, and parent waits. `main` sets up a pipe, runs `test` in a child with stdout redirected to the pipe, reads three lines, verifies their order, and reports success/failure.

Control flow: expected line order is child signal announcement, parent signal handler output, child exit announcement. The bug under test swaps the last two lines if wait is mishandled by tracing.

State and persistence: pipe and process state only.

Dependencies and integration: POSIX signals, fork/wait, pipes, and strace follow-fork behavior.

Risks: uses `signal()` with restart semantics and sleeps for ordering; slow systems can affect timing. Test signals: under `strace -f`, program should print "Good: wait seems to be correctly interrupted by signals".
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/wait_must_be_interruptible.c -->
