<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev.c -->
# sources/test-tools/strace/tests/ioctl_evdev.c

Purpose: `ioctl_evdev.c` evdev ioctl decoder test for failure-side command and structure argument rendering. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are EVIOCGVERSION, EVIOCGEFFECTS, EVIOCGRAB, EVIOCREVOKE, EVIOCSCLOCKID, EVIOCGID, EVIOCGREP/EVIOCSREP, EVIOCGKEYCODE/EVIOCSKEYCODE, EVIOCGKEYCODE_V2/EVIOCSKEYCODE_V2, EVIOCGABS/EVIOCSABS, EVIOCGBIT/KEY/LED/SND/SW/PROP, EVIOCSFF/EVIOCRMFF, struct ff_effect and input structs. Local include directives/macros observed in this source are `tests.h, errno.h, inttypes.h, stdio.h, string.h, sys/ioctl.h, linux/ioctl.h, linux/input.h` and `TEST_NULL_ARG_EX=(cmd, str)					\, TEST_NULL_ARG=(cmd) TEST_NULL_ARG_EX(cmd, #cmd)`. Locally visible function entry points include `print_envelope, print_ffe_common, main`.

Control flow: main first exercises NULL/no-arg commands, then uses helper printers for force-feedback envelopes/effects and a series of input/event structures and unknown values; VERBOSE controls whether large arrays and nested FF fields are expanded. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; local/tail-allocated objects carry deterministic magic values. XLAT and VERBOSE macros alter expected symbolic and sequence detail. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, sys/ioctl.h, XLAT helpers, errno/inttypes/string. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: input-event UAPI growth, force-feedback union layout, abbreviated sequence limits, and xlat mode differences are the main drift points. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers null arguments, bad pointers, known/unknown event/key/abs symbols, FF effect structures, and verbose array expansion. This file has 289 source lines and 8144 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev.c -->
