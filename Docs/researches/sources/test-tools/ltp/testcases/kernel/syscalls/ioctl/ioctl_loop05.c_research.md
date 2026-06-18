# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_loop05.c

Purpose: `LOOP_SET_DIRECT_IO` mode toggles and alignment-sensitive offset behavior. Source comment intent: Copyright (c) 2020 FUJITSU LIMITED. All rights reserved. Copyright (c) Linux Test Project, 2020-2022 Author: Yang Xu <xuyang2018.jy@cn.jujitsu.com>.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `check_dio_value`, `verify_ioctl_loop`, `setup`, `cleanup`; key constants/macros `DIO_MESSAGE`, `NON_DIO_MESSAGE`; local structs `loop_info`, `loop_info`, `tst_test`; headers `stdio.h`, `unistd.h`, `string.h`, `stdlib.h`, `sys/mount.h`, `lapi/loop.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: creates temporary backing files and loop-device attachments, then checks sysfs and ioctl-visible loop state before detaching.

Dependencies and integration points: integrates with loop-control ioctls, backing files, sysfs state, and root-only block-device behavior. Harness metadata `cleanup, needs_kconfigs, needs_root, needs_tmpdir, setup, skip_filesystems, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Requires root and block-device/loop support; failures can reflect environment setup as well as kernel regressions.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
