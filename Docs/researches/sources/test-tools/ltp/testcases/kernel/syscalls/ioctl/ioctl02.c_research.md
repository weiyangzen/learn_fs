# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl02.c

Purpose: TTY `TCGETA`/`TCGETS` and `TCSETA`/`TCSETS` round-trip checks using a parent/child tty device workflow. Source comment intent: Test TCGETA/TCGETS and TCSETA/TCSETS ioctl implementations for tty driver. In this test, the parent and child open the parentty and the childtty respectively. After opening the childtty the child flushes the stream and wakes the parent (thereby asking it to continue its testing). The parent, then starts the testing. It issues a TCGETA/TCGETS ioctl to get all the tty parameters. It then changes them to known values by issuing a TCSETA/TCSETS ioctl. Then the parent issues a TCSETA/TCGETS ioctl again and compares the received values with what it had set earlier. The test fails if TCGETA/TCGETS or TCSETA/TCSETS fails, or if the received values don't match those that were set. The parent does all.

Important APIs/types/functions: core calls `SAFE_OPEN`, `SAFE_IOCTL`; local functions `do_child`, `prepare_termio`, `run_ptest`, `chk_tty_parms_termio`, `chk_tty_parms_termios`, `setup`, `cleanup`, `verify_ioctl`, `prepare_termio`, `run_ptest`, `cmp_attr`, `cmp_c_cc`, `chk_tty_parms_termio`, `chk_tty_parms_termios`, `do_child`, `setup`, `cleanup`; key constants/macros `CMP_ATTR`, `CMP_C_CC`; local structs `termio`, `termios`, `variant`, `variant`, `tst_test`; headers `stdio.h`, `stdlib.h`, `asm/termbits.h`, `lapi/ioctl.h`, `tst_test.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `cleanup, forks_child, needs_checkpoints, needs_root, options, setup, test_all, test_variants, timeout` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Variant coverage depends on syscall availability and kernel time ABI support.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
