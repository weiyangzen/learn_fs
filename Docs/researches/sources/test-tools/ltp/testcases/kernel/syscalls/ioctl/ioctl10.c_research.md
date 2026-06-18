# sources/test-tools/ltp/testcases/kernel/syscalls/ioctl/ioctl10.c

Purpose: `PROCMAP_QUERY` ioctl coverage for exact VMA lookup, no-match ENOENT, next-VMA lookup, writable filtering, and VMA name export. Source comment intent: Test PROCMAP_QUERY :manpage:`ioctl(2)` for /proc/$PID/maps. Test based on :kselftest:`proc/proc-pid-vm.c`. - ioctl with exact match query_addr - ioctl without match query_addr - check COVERING_OR_NEXT_VMA query_flags - check PROCMAP_QUERY_VMA_WRITABLE query_flags - check vma_name_addr content.

Important APIs/types/functions: core calls `ioctl`, `SAFE_OPEN`; local functions `parse_vm_flags`, `parse_maps_file`, `verify_ioctl`, `setup`, `cleanup`; key constants/macros `PROC_MAP_PATH`; local structs `map_entry`, `procmap_query`, `map_entry`, `procmap_query`, `tst_test`; headers `config.h`, `stdlib.h`, `sys/ioctl.h`, `errno.h`, `fnmatch.h`, `tst_test.h`, `tst_safe_stdio.h`, `sys/sysmacros.h`, `linux/fs.h`, `lapi/ioctl.h`.

Control flow: `setup` prepares kernel objects, files, namespaces, queues, descriptors, or feature probes; the main run/verify function executes the syscall scenario and compares return values, errno, metadata, or data contents; `cleanup` releases descriptors and removes IPC/loop/fs resources.

State and persistence behavior: state is mostly transient file descriptor, process, or procfs/ioctl query data managed by the LTP harness.

Dependencies and integration points: integrates with device- or procfs-specific ioctl contracts and errno behavior. Harness metadata `bufs, cleanup, setup, test_all` controls tmpdirs, root requirements, kconfig checks, buffers, variants, checkpoints, mount devices, or cleanup.

Risks: Primary risks are environment-dependent TCONF paths and errno/message expectations that can shift with kernel behavior.

Test signals: TPASS is emitted when the expected return value, errno, metadata, data integrity, or resource state matches; TFAIL/TBROK/TCONF distinguish regression, harness/setup failure, or unsupported kernel/environment.
