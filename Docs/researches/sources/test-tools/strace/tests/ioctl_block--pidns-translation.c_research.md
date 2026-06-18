<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_block--pidns-translation.c -->
# sources/test-tools/strace/tests/ioctl_block--pidns-translation.c

Purpose: `ioctl_block--pidns-translation.c` block-device ioctl decoder test including scalar, pointer, partition, trace setup, and pid namespace translation cases. Wrapper chain: ioctl_block--pidns-translation.c -> ioctl_block.c. Variant effect: PIDNS_TRANSLATION enables pid namespace leader/pid translation expectations.

Important APIs/types/functions: Primary APIs and data surfaces are BLKBSZGET, BLKBSZSET, BLKPG, BLKDISCARD, BLKSECDISCARD, BLKZEROOUT, BLKTRACESETUP, BLKRRPART, BLKFLSBUF, BLKTRACESTART, BLKTRACESTOP, BLKTRACETEARDOWN, struct blkpg_ioctl_arg, blkpg_partition, blk_user_trace_setup. Local include directives/macros observed in this source are `ioctl_block.c` and `PIDNS_TRANSLATION=#include "ioctl_block.c"`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: PIDNS_TEST_INIT sets namespace context, TEST_NULL_ARG emits NULL cases, then main prints scalar settings, int pointer settings, uint64 pairs, BLKPG resize/add partition payloads, BLKTRACESETUP with getpid, argless commands through xlat_data, and an unknown 0x12 ioctl. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_block.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistent state; pidns helpers affect printed leader and pid translation text, tail allocations provide stable payload addresses. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, pidns.h, linux/fs.h, linux/blkpg.h, linux/blkzoned.h, linux/blktrace_api.h, xlat.h. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: pid namespace text is environment-sensitive, block UAPI structures may vary, and argless command classification must stay aligned with strace decoders. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output covers NULL handling, decoded arrays/structs, pid translation suffix, command names, and unknown _IOC fallback. This file has 3 source lines and 51 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_block--pidns-translation.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_block--pidns-translation.c -->
