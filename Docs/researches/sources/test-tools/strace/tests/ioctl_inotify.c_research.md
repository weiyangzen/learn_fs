<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_inotify.c -->
# sources/test-tools/strace/tests/ioctl_inotify.c

Purpose: `ioctl_inotify.c` inotify ioctl decoder test for INOTIFY_IOC_SETNEXTWD and unknown inotify command formatting. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, INOTIFY_IOC_SETNEXTWD, _IOC macros, int32_t watch-descriptor argument. Local include directives/macros observed in this source are `tests.h, inttypes.h, stdio.h, string.h, unistd.h, scno.h, linux/ioctl.h` and `implementation defaults`. Locally visible function entry points include `sys_ioctl, main`.

Control flow: main sends a crafted unknown inotify command, INOTIFY_IOC_SETNEXTWD+1, then INOTIFY_IOC_SETNEXTWD with a magic argument and prints expected generic or symbolic decoding. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_inotify.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; constants are local and the syscall is always against fd -1. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/ioctl.h; provides fallback definition for INOTIFY_IOC_SETNEXTWD. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: command fallback text depends on _IOC bit layout and host headers; signed truncation of magic to int is intentional. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected EBADF output validates unknown _IOC decomposition and signed integer argument printing for SETNEXTWD. This file has 61 source lines and 1622 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_inotify.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_inotify.c -->
