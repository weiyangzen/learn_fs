# sources/test-tools/syzkaller/executor/executor_linux.h

Purpose: Linux executor adapter for memory layout, syscall dispatch, KCOV/remote coverage, pkey protection, process exit, and feature probing.

Important APIs and control flow: `os_init` sets parent-death signal, maps guard/data pages, installs SIGCHLD handling, and probes reserved pkey availability. `execute_syscall` calls pseudo-syscalls or raw `syscall`. KCOV flow is `cover_open` -> `cover_mmap` -> `cover_enable` -> `cover_reset`/`cover_collect` -> optional `cover_close`; it supports 32/64-bit traces, comparison mode, delayed mmap, remote common/USB handles, read-only reset ioctl, and guard pages. `doexit` and `doexit_thread` use raw exit syscalls and then spin to survive blocked exits. Feature probes include KCSAN filtering, NIC VF/devlink PCI presence, delayed KCOV mmap, KCOV reset ioctl, kdump setup, fault/leak/USB/LRWPAN/binfmt/swap hooks.

State and dependencies: global `pkeys_enabled` affects coverage write protection. `cover_t` carries fd, mmap allocation, data pointers, offsets, and enabled state. The feature table maps `rpc::Feature` values to setup functions.

Integration points: included by `executor.cc` for Linux, consumed by runner handshake feature negotiation, snapshot pkey setup, and tests.

Risks and tests: KCOV ioctl behavior varies by kernel; setup functions return user-readable reasons for unsupported features. `setup_delay_kcov` deliberately tests for missing mappings via `clock_gettime` EFAULT. Kdump setup shells out to `kexec` and parses `/proc/cmdline`. Tests include Linux KVM/SYZOS helpers plus syzkaller machine checks.
