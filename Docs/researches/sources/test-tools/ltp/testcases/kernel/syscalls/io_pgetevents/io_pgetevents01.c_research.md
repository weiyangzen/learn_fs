# sources/test-tools/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents01.c

Purpose: successful `io_pgetevents` completion of a single pwrite request across old-timespec and time64 syscall variants. Source comment intent: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> Description: Basic io_pgetevents() test to receive 1 event successfully..

Important APIs/types/functions: core calls `io_pgetevents`, `io_setup`, `io_submit`, `io_destroy`, `SAFE_OPEN`; local functions `setup`, `run`; local structs `time64_variants`, `time64_variants`, `io_event`, `iocb`, `tst_ts`, `tst_test`; headers `time64_variants.h`, `tst_test.h`, `tst_timer.h`, `lapi/io_pgetevents.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with the AIO completion path, optional signal-mask replacement, and 32-bit/time64 timeout ABI variants. Harness metadata `min_kver, needs_tmpdir, setup, test_all, test_variants` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
