<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/sig.c -->
# sources/test-tools/strace/attic/test/sig.c

Purpose: small signal interruption reproducer for read/write tracing.

Important functions: `interrupt()` writes `xyzzy\n` to stderr. `main` installs it for `SIGINT`, blocks in `read(0, buf, 1024)`, then writes `qwerty\n` to stderr.

Control flow: waits for stdin or signal. If SIGINT interrupts or restarts the read depending on system semantics, output sequence changes.

State and persistence: no persistent state; only signal handler state and stdio writes.

Dependencies and integration: POSIX signal/read/write, used manually under strace.

Risks: old-style `signal()` semantics vary and handler signature lacks the conventional `int` parameter. Test signals: send SIGINT while traced and verify strace reports interrupted/restarted read behavior clearly.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/sig.c -->
