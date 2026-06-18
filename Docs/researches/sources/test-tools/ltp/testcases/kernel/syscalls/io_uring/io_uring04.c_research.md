# sources/test-tools/ltp/testcases/kernel/syscalls/io_uring/io_uring04.c

Purpose: CVE-2026-43494 PinTheft/RDS zerocopy page-pin accounting regression using fixed and cloned io_uring buffers. Source comment intent: CVE-2026-43494 Test for PinTheft, fixed by: e17492979319 ("net/rds: reset op_nents when zerocopy page pin fails"). The bug is in the RDS zerocopy send error path. When RDS pins user pages for zerocopy send and a later page faults, the error cleanup can drop references for pages that are later released again during RDS message cleanup. This corrupts page reference accounting. The public exploit combines this RDS reference-counting bug with io_uring fixed buffers and cloned buffer registrations to turn stale page references into a page-cache overwrite and local privilege escalation. This test does not attempt privilege escalation. It triggers the underlying RDS zerocopy failure path by sending.

Important APIs/types/functions: core calls `io_uring_setup`, `io_uring_register`; local functions `clone_buffers`, `setup`, `trigger`, `poke_rss_accounting`, `run`, `cleanup`; key constants/macros `CLEANUP_WAIT_SECS`, `RSS_CHECK_CHILDREN`, `RSS_CHECK_SIZE`, `GUP_PIN_COUNTING_BIAS`; local structs `io_uring_clone_buffers`, `io_uring_params`, `iovec`, `sockaddr_in`, `sockaddr_in`, `cmsghdr`, `iovec`, `msghdr`; headers `stdint.h`, `tst_test.h`, `lapi/io_uring.h`, `lapi/rds.h`, `lapi/socket.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: maps ring buffers and may register fixed buffers; file, socket, RDS, and taint state are cleaned up after the test.

Dependencies and integration points: integrates with ring setup, registration, submission/completion queues, and kernel feature gating. Harness metadata `cleanup, forks_child, needs_kconfigs, save_restore, setup, tags, test_all, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: This is stress/security-sensitive coverage and can expose kernel taint, crashes, or long runtimes on vulnerable or underprovisioned systems.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
