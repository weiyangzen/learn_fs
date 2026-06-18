<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/sigkill_rain.c -->
# sources/test-tools/strace/attic/test/sigkill_rain.c

Purpose: stress reproducer for strace handling of processes killed while syscalls are being entered or decoded.

Important logic: parent blocks SIGCHLD and loops. Each child repeatedly forks a grandchild that kills the child with SIGKILL while the child either does nothing or calls `sendto(-1, ...)`; parent waits each round. It prints instructions to inspect strace logs for bad interrupted syscall decoding.

Control flow: nested fork/kill loops create races between syscall decoding and task death.

State and persistence: no files written by the program, but intended strace usage writes logs.

Dependencies and integration: Linux process signaling, sockets, wait, and strace `-f -oLOG`.

Risks: intentionally racy and resource-intensive; large loop counts can stress process tables. Output validation is manual grep-based. Test signals: strace log should not contain undecodable placeholders such as unavailable syscall data for the tested paths.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/sigkill_rain.c -->
