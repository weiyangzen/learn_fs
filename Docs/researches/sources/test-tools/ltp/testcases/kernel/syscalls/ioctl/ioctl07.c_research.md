# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl07.c

Purpose: random entropy count comparison between `RNDGETENTCNT` and `/proc/sys/kernel/random/entropy_avail`. Source comment intent: Very basic test for the RND* :manpage:`ioctl(2)`. Reads the entropy available from both /proc and the ioctl and compares they are similar enough (within a configured fuzz factor)..

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`, `SAFE_IOCTL`; local functions `verify_ioctl`, `setup`, `cleanup`; local structs `tst_test`; headers `asm/types.h`, `linux/random.h`, `stdlib.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, options, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
