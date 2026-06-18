<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/clone.c -->
# sources/test-tools/strace/attic/test/clone.c

Purpose: minimal Linux `clone(2)` reproducer for tracing a clone sharing VM, filesystem, and file descriptor state.

Important functions: `child(void *)` writes `clone\n`. `main` allocates a stack buffer, calls `clone(child, stack+4000, CLONE_VM|CLONE_FS|CLONE_FILES, NULL)`, writes `original\n`, and exits.

Control flow: parent and clone child run concurrently without waiting. Shared VM and file tables exercise strace clone handling.

State and persistence: only process state and stdout writes; no files are persisted.

Dependencies and integration: requires `_GNU_SOURCE`, Linux `sched.h`, and `clone`.

Risks: manual stack pointer `stack+4000` is crude and architecture alignment-sensitive. No error checking on `clone` or `write`. Output order is nondeterministic. Test signals: under strace, both clone child and original process writes should be visible.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/clone.c -->
