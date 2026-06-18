# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring02.c

Purpose: CVE-2020-29373 regression that async `SENDMSG` must not bypass a process chroot. Source comment intent: Copyright (C) 2021 SUSE LLC Author: Nicolai Stange <nstange@suse.de> LTP port: Martin Doucha <mdoucha@suse.cz> CVE-2020-29373 Check that io_uring does not bypass chroot. Fixed in: commit 9392a27d88b9707145d713654eb26f0c29789e50 Author: Jens Axboe <axboe@kernel.dk> Date: Thu Feb 6 21:42:51 2020 -0700 io-wq: add support for inheriting ->fs commit ff002b30181d30cdfbca316dadd099c3ca0d739c Author: Jens Axboe <axboe@kernel.dk> Date: Fri Feb 7 16:05:21 2020 -0700 io_uring: grab ->fs as part of async preparation stable 5.4 specific backport: commit c4a23c852e80a3921f56c6fbc851a21c84a6d06b Author: Nicolai Stange <nstange@suse.de> Date: Wed Jan 27 14:34:43 2021 +0100.

Important APIs/types/functions: local functions `setup`, `drain_fallback`, `check_result`, `run`, `cleanup`; key constants/macros `CHROOT_DIR`, `SOCK_NAME`, `SPAM_MARK`, `BEEF_MARK`; local structs `sockaddr_un`, `io_uring_params`, `tst_io_uring`, `iovec`, `msghdr`, `msghdr`, `io_uring_sqe`, `io_uring_sqe`; headers `stdio.h`, `sys/socket.h`, `sys/un.h`, `tst_test.h`, `tst_safe_io_uring.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `caps, cleanup, needs_tmpdir, save_restore, setup, tags, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
