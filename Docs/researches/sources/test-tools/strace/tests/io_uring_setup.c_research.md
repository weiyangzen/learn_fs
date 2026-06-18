<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_setup.c -->
# sources/test-tools/strace/tests/io_uring_setup.c

Purpose: `io_uring_setup.c` checks strace decoding of the io_uring_setup syscall and struct io_uring_params. This is the primary implementation body; no wrapper macros are layered on top of the source beyond its own defaults.

Important APIs/types/functions: Primary APIs and data surfaces are __NR_io_uring_setup, struct io_uring_params, sq_off/cq_off nested offsets, IORING_SETUP_* flags, IORING_FEAT_* feature flags. Local include directives/macros observed in this source are `tests.h, scno.h, fcntl.h, stdio.h, stdint.h, string.h, unistd.h, kernel_time_types.h, linux/io_uring.h, sys/stat.h, sys/types.h, print_fields.h` and `UAPI_LINUX_IO_URING_H_SKIP_LINUX_TIME_TYPES_H=#include <linux/io_uring.h>`. Locally visible function entry points include `sys_io_uring_setup, main`.

Control flow: sys_io_uring_setup wraps the raw syscall with poisoned upper arguments. main tests NULL, bad pointer, all-flags/reserved-field input, then zeroed normal parameter blocks with and without IORING_SETUP_ATTACH_WQ referencing /dev/full. For wrapper sources, preprocessing first applies the listed macros and then compiles the included base body; runtime control flow is therefore inherited from `io_uring_setup.c` with only the selected xlat, verbosity, injection, pid namespace, or string-length behavior changed.

State and persistence behavior: no persistence; errstr records each syscall result and kernel-mutated params are printed only when setup succeeds. The tests intentionally avoid durable state; they rely on deterministic local buffers, tail-page allocation, raw syscall/ioctl return capture, and expected-output printing for the strace test harness.

Dependencies and integration points: tests.h, scno.h, linux/io_uring.h, kernel_time_types.h, print_fields.h, xlat/uring_setup_features.h, /proc/self/fd, /dev/full. Integration is through strace's testsuite: the compiled binary prints the expected trace, the shell harness or test runner captures strace output, and reconciliation compares symbolic ioctl/syscall decoder output against these expectations.

Risks: kernel/header drift for newly added setup flags, success path differences on hosts that allow io_uring_setup, and fd-path annotation dependence. Wrapper files add risk that the include chain, macro value, or test name drifts from the harness entry that invokes it, producing correct C but mismatched expected output.

Test signals: Exact stdout verifies flag decoding, reserved arrays, wq_fd path display, anon_inode return rendering, and fallback pointer printing on failure. This file has 148 source lines and 4433 bytes; non-empty generated research at the mirrored `Docs/researches/sources/test-tools/strace/tests/io_uring_setup.c_research.md` path is the worker-produced signal for this source item.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/io_uring_setup.c -->
