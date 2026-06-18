# sources/test-tools/ltp/testcases/kernel/syscalls/ioprio/ioprio.h

Purpose: shared wrappers and validation helpers around raw `ioprio_get`/`ioprio_set` syscalls. Source comment intent: Copyright (c) 2019 Linus Walleij <linus.walleij@linaro.org> Copyright (c) 2023 Linux Test Project.

Important APIs/types/functions: local functions `sys_ioprio_get`, `sys_ioprio_set`, `prio_in_range`, `class_in_range`, `ioprio_check_setting`; key constants/macros `LTP_IOPRIO_H`; headers `lapi/ioprio.h`, `lapi/syscalls.h`.

Control flow: helper-only flow; callers invoke these inline wrappers from neighboring tests.

State and persistence behavior: updates current-process I/O priority and validates the kernel-reported encoded class/priority value.

Dependencies and integration points: integrates with I/O priority syscall wrappers, class/priority encoding, and readback validation. Harness metadata `none explicit` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
