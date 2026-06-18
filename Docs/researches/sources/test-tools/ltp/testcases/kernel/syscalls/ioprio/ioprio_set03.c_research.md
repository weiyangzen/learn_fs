# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio_set03.c

Purpose: invalid priority values must fail without changing the prior effective priority. Source comment intent: Copyright (c) 2019 Linus Walleij <linus.walleij@linaro.org> Copyright (c) 2023 Linux Test Project.

Important APIs/types/functions: core calls `ioprio_set`; local functions `run`; local structs `tst_test`; headers `tst_test.h`, `ioprio.h`.

Control flow: the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents.

State and persistence behavior: creates AIO contexts and temporary files/pipes, then destroys contexts and closes descriptors to avoid leaking kernel AIO state.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation. Harness metadata `test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
