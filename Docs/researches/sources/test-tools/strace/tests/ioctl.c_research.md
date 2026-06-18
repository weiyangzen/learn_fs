<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl.c -->
# sources/test-tools/strace/tests/ioctl.c

Purpose: `ioctl.c` broad smoke test for ioctl command-number decoding across multiple Linux subsystems. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, TCGETS, MMTIMER_GETRES, VIDIOC_ENUMINPUT, HIDIOCGVERSION, HIDIOCGPHYS, EVIOCGBIT, mixer/MTD overlap, raw _IOC commands, ZFS_IOC_* aliases, BLKZNAME, KSTAT_IOC_CHAIN_ID. Local include directives/macros observed in this source are `tests.h, fcntl.h, stdio.h, stdint.h, unistd.h, termios.h, sys/ioctl.h, linux/hiddev.h, linux/input.h, linux/mmtimer.h, linux/videodev2.h` and `implementation defaults`. Locally visible function entry points include `main`.

Control flow: main issues ioctl calls on fd -1 against representative command numbers and prints the symbolic or fallback command form expected from strace. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local uint64_t and optional termios struct only supply stable pointers. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, termios.h, sys/ioctl.h, linux/hiddev.h, linux/input.h, linux/mmtimer.h, linux/videodev2.h; TCGETS is skipped on POWERPC. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: alias collisions are intentional and can drift with headers; architecture-specific termios encoding and new command tables can alter printed names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact EBADF lines with expected aliases and generic _IOC fallback formatting. This file has 76 source lines and 2052 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl.c -->
