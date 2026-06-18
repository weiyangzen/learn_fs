# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop06.c

Purpose: invalid loop block-size rejection through `LOOP_SET_BLOCK_SIZE` and `LOOP_CONFIGURE`. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `verify_ioctl_loop`, `run`, `setup`, `cleanup`; local structs `loop_config`, `tcase`, `tcase`, `tst_test`; headers `stdio.h`, `unistd.h`, `sys/types.h`, `stdlib.h`, `lapi/blkdev.h`, `lapi/loop.h`, `tst_fs.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, tcnt, test` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
