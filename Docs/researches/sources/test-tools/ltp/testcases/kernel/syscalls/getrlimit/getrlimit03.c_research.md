<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit03.c

Purpose: Architectures may provide up to three syscalls that have been used to implement getrlimit(2) in different libc implementations. These syscalls differ in the size and signedness of rlim_t: - __NR_getrlimit uses long or unsigned long, depending on the architecture - __NR_ugetrlimit uses unsigned long, and only exists on architectures where __NR_getrlimit is signed - __NR_prlimit64 uses uint64_t This test compares the results returned by all three syscalls, confirming that they either match or were appropriately cappe

Important APIs/types/functions: includes `inttypes.h`, `stdint.h`, `sys/time.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`, `lapi/abisize.h`; touches `getrlimit`, `raw syscall path`; defines `getrlimit_u64`, `getrlimit_ulong`, `getrlimit_long`, `compare_retval`, `compare_u64_ulong`, `compare_u64_long`, `run`.

Control flow centers on `getrlimit_u64`, `getrlimit_ulong`, `getrlimit_long`, `compare_retval`, `compare_u64_ulong`, `compare_u64_long`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test` into the LTP runner. Error-path assertions cover `EABI`, `ENOSYS`.

State and persistence behavior: Runtime state is per-process resource limit structures and architecture-specific syscall ABI representations.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `inttypes.h`, `stdint.h`, `sys/time.h`, `sys/resource.h`, `tst_test.h`, `lapi/syscalls.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TCONF`, `TFAIL`, `TPASS`, `TST_ABI32`. Expected errno values include `EABI`, `ENOSYS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/getrlimit/getrlimit03.c -->
