<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c

Purpose: `ioctl_counter-Xabbrev.c` COUNTER_* ioctl decoder test for Linux counter watch management and unknown counter command numbers. Wrapper chain: ioctl_counter-Xabbrev.c -> ioctl_counter.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_ioctl, COUNTER_ADD_WATCH_IOCTL, COUNTER_ENABLE_EVENTS_IOCTL, COUNTER_DISABLE_EVENTS_IOCTL, struct counter_watch, counter component/scope/event enums, _IOC. Local include directives/macros observed in this source are `ioctl_counter.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: main iterates all ioctl directions and sizes for unknown counter commands, then checks NULL, bad pointer, known watch, mixed known watch, unknown enum watch, and enable/disable no-argument commands. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_counter.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr captures each EBADF result and one tail-allocated counter_watch is mutated for cases. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/ioctl.h, linux/counter.h, XLAT_* mode macros. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: counter enum additions, platform _IOC type differences, and xlat raw/verbose/abbrev rendering changes affect expectations. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout validates command-number formatting, enum known/unknown rendering, bad pointer handling, and no-argument command decoding. This file has 3 source lines and 49 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_counter-Xabbrev.c -->
