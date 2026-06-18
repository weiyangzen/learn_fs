<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo03.c

Purpose: Test if CLOCK_BOOTTIME namespace offset is applied to sysinfo uptime and that it's consistent with /proc/uptime as well. After a call to unshare(CLONE_NEWTIME) a new timer namespace is created, the process that has called the unshare() can adjust offsets for CLOCK_MONOTONIC and CLOCK_BOOTTIME for its children by writing to the '/proc/self/timens_offsets'.

Important APIs/types/functions: includes `sys/sysinfo.h`, `lapi/posix_clocks.h`, `tst_test.h`, `lapi/sched.h`; exercises `sysinfo`, `unshare`; defines `read_proc_uptime`, `verify_sysinfo`; uses constants `CLOCK_BOOTTIME`, `CLOCK_MONOTONIC`, `CLONE_NEWTIME`.

Control flow centers on `read_proc_uptime`, `verify_sysinfo`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.needs_root`, `.needs_kconfigs`, `.tags` into the runner. Named case hints include `CONFIG_TIME_NS=y`, `linux-git`.

State and persistence behavior: Runtime state is global memory, swap, process, load, and uptime counters returned in `struct sysinfo`.

Dependencies and integration points: Depends on `sysinfo(2)`, `/proc`-like global accounting consistency, and architecture-compatible `struct sysinfo` layout. Direct include dependencies include `sys/sysinfo.h`, `lapi/posix_clocks.h`, `tst_test.h`, `lapi/sched.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sysinfo/sysinfo03.c -->
