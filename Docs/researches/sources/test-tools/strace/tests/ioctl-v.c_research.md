<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-v.c -->
# sources/test-tools/strace/tests/ioctl-v.c

Purpose: `ioctl-v.c` generic verbose ioctl payload test for _IOC read/write direction and data-size decoding. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, _IOC, _IOR, _IOW, _IOWR, RVAL_EBADF, kernel_ulong_t. Local include directives/macros observed in this source are `tests.h, stdio.h, unistd.h, sys/ioctl.h` and `implementation defaults`. Locally visible function entry points include `main`.

Control flow: main uses an eight-byte byte array and issues zero-size read/write commands, read, write, bidirectional, _IOC_NONE-with-size, and bad-pointer cases, printing the exact verbose data representation expected from strace. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl-v.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local array contents are fixed and reused for expected input/output strings. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, sys/ioctl.h, unistd.h, stdio.h. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: depends on strace -v style data printing, _IOC encoding width, and correct handling of bad pointer versus readable local array. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout should show quoted byte strings for readable arguments and raw %#lx for invalid pointers. This file has 58 source lines and 1818 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl-v.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl-v.c -->
