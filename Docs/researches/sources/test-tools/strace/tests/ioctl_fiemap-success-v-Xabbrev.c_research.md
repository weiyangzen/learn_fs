<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c -->
# sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c

Purpose: `ioctl_fiemap-success-v-Xabbrev.c` FS_IOC_FIEMAP decoder test for fiemap request and returned extents. Wrapper chain: ioctl_fiemap-success-v-Xabbrev.c -> ioctl_fiemap-success-v.c -> ioctl_fiemap-success.c -> ioctl_fiemap.c. Variant effect: XLAT_ABBREV/default xlat rendering keeps symbolic abbreviated output; VERBOSE expands nested structures, arrays, strings, or long returned buffers; INJECT_RETVAL enables the syscall-injection success path and appends injected return markers.

Important APIs/types/functions: Primary APIs and data surfaces are FS_IOC_FIEMAP, struct fiemap, fiemap_extent, FIEMAP_FLAG_* and FIEMAP_EXTENT_* flags. Local include directives/macros observed in this source are `ioctl_fiemap-success-v.c` and `XLAT_ABBREV=1`. Locally visible function entry points include `none in wrapper; inherited main/control flow from included implementation`.

Control flow: optional injection skip locks onto a successful FIEMAP call, then main checks bad pointer, valid request flags, success/failure split for mapped_extents, and a two-extent returned payload with known and unknown extent flags. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `ioctl_fiemap.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr is updated per ioctl and allocated fiemap payloads are mutated between cases. VERBOSE controls whether returned extents are expanded. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, linux/fiemap.h, linux/fs.h, sys/ioctl.h, ioctl-success.sh for injected variants. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: fiemap flag additions and host success/failure behavior can alter returned-side printing; verbose mode must track nested extent truncation. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Expected output validates bad pointers, request fields, flag xlat known/unknown handling, injected suffixes, and verbose extent arrays. This file has 3 source lines and 58 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_fiemap-success-v-Xabbrev.c -->
