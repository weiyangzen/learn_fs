<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/attic/test/procpollable.c -->
# sources/test-tools/strace/attic/test/procpollable.c

Purpose: legacy `/proc` pollability test for systems exposing process control via procfs ioctls.

Important logic: forks a child that pauses; parent opens `/proc/<pid>` read/write, issues `PIOCSTOP`, polls for `POLLPRI`, then kills child. Failures kill the child and exit 1.

Control flow: parent/child split with a single procfs control and poll path.

State and persistence: modifies child process stopped/killed state; no files written.

Dependencies and integration: depends on old `<sys/procfs.h>` and `<sys/stropts.h>` interfaces not available on many modern Linux systems.

Risks: highly platform-specific and likely obsolete. Missing includes for `fork`, `ioctl`, and `kill` prototypes on strict compilers may warn/fail. Test signals: on supported systems, `poll` should report `POLLPRI` after stopping the child.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/attic/test/procpollable.c -->
