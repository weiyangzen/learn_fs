<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll.c -->
# sources/test-tools/strace/tests/ioctl_epoll.c

Purpose: `ioctl_epoll.c` EPIOC* ioctl decoder test for epoll busy-poll parameters and unknown epoll command formatting. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, EPIOCSPARAMS, EPIOCGPARAMS, struct epoll_params, _IOC direction/type/number/size macros. Local include directives/macros observed in this source are `tests.h, scno.h, errno.h, inttypes.h, stdio.h, stdlib.h, string.h, unistd.h, linux/ioctl.h, linux/eventpoll.h` and `implementation defaults`. Locally visible function entry points include `sys_ioctl, main`.

Control flow: optional INJECT_RETVAL mode first locks onto a successful injected EPIOCSPARAMS call; main then iterates unknown command-number combinations and tests NULL, bad pointer, and several epoll_params payloads for set/get commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_epoll.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr plus optional injected marker. In non-injected mode EPIOCGPARAMS is printed as a pointer on failure; injected mode prints structure contents. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/eventpoll.h, linux/ioctl.h, XLAT mode macros, ioctl-success.sh for success variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: EPIOC constants are recent and header-dependent; injected retval in this file is hard-checked against 42 in the lock loop despite wrapper defining INJECT_RETVAL 1, so harness coordination matters. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output checks raw/verbose/abbrev command xlat, time comments for busy_poll_usecs, __pad display, and injected suffixes. This file has 173 source lines and 4195 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_epoll.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_epoll.c -->
