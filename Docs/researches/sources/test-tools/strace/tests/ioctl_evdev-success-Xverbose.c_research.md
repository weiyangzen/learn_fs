<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c -->
# sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c

Purpose: `ioctl_evdev-success-Xverbose.c` success-injection evdev decoder test for output-side EVIOCG* structure and bitset decoding. Wrapper chain: ioctl_evdev-success-Xverbose.c -> ioctl_evdev-success.c. Variant effect: XLAT_VERBOSE selects numeric plus symbolic xlat rendering.

Important APIs/types/functions: Primary APIs and data surfaces are ioctl, EVIOCGID, EVIOCGABS, EVIOCGBIT, EVIOCGMTSLOTS, struct input_id, input_absinfo, long bit arrays, print_fields helpers. Local include directives/macros observed in this source are `ioctl_evdev-success.c` and `XLAT_VERBOSE=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: without arguments main returns 0 for harness probing; with NUM_SKIP and INJECT_RETVAL it locks onto injected EVIOCGID, prepares id/absinfo/slot/bitset buffers, then test_evdev invokes each command and printer to emit input/output expectations. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_evdev-success.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is global, and local arrays are sized so injected return values cap bitset decoding. VERBOSE and XLAT modes change bit names and comments. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/input.h, print_fields.h, ioctl-success.sh harness, XLAT macros, tail_alloc/fill_memory helpers. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: requires syscall injection and a nonnegative retval; bitset output depends on word size and injected byte count; evdev enum additions change xlat names. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Pass signal is exact injected-output comparison for input_id, variable-size absinfo, EVIOCGBIT truncation, KEY_F12 visibility, mtslots, and invalid ABS_MT names. This file has 3 source lines and 56 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_evdev-success-Xverbose.c -->
