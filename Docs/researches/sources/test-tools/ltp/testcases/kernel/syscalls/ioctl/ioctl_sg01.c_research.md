# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl_sg01.c

Purpose: CVE-2018-1000204 `SG_IO` leak regression using a readable generic SCSI device and zeroed output buffer checks. Source comment intent: CVE-2018-1000204 Test ioctl(SG_IO) and check that kernel doesn't leak data. Requires a read-accessible generic SCSI device (e.g. a DVD drive). Leak fixed in: commit a45b599ad808c3c982fdcdc12b0b8611c2f92824 Author: Alexander Potapenko <glider@google.com> Date: Fri May 18 16:23:18 2018 +0200 scsi: sg: allocate with __GFP_ZERO in sg_build_indirect() commit 41e99fe2005182139b1058db71f0d241f8f0078c Author: Desnes Nunes <desnesn@redhat.com> Date: Fri Oct 31 01:34:36 2025 -0300 usb: storage: Fix memory leak in USB bulk transport.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `dump_hex`, `setup`, `cleanup`, `run`; key constants/macros `SYSDIR`, `BLOCKDIR`, `BUF_SIZE`, `CMD_SIZE`; local structs `sg_io_hdr`, `dirent`, `tst_test`; headers `sys/types.h`, `dirent.h`, `fcntl.h`, `unistd.h`, `ctype.h`, `scsi/sg.h`, `sys/ioctl.h`, `stdio.h`, `tst_test.h`, `tst_memutils.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, setup, tags, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: This is stress/security-sensitive coverage and can expose kernel taint, crashes, or long runtimes on vulnerable or underprovisioned systems.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
