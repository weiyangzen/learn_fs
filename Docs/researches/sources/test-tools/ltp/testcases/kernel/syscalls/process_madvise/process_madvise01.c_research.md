<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise01.c

Purpose: Allocate anonymous memory pages inside child and reclaim it with MADV_PAGEOUT. Then check if memory pages have been swapped out by looking at smaps information. The advice might be ignored for some pages in the range when it is not applicable, so test passes if swap memory increases after reclaiming memory with MADV_PAGEOUT.

Important APIs/types/functions: includes `sys/mman.h`, `tst_test.h`, `lapi/mmap.h`, `lapi/syscalls.h`, `process_madvise.h`; exercises `process_madvise`, `mmap`, `raw syscall path`; defines `child_alloc`, `setup`, `cleanup`, `run`.

Control flow centers on `child_alloc`, `setup`, `cleanup`, `run`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test_all`, `.forks_child`, `.needs_root` into the LTP runner. Named case hints include `memory`, `CONFIG_SWAP=y`.

State and persistence behavior: Runtime state is a remote process address space referenced through pidfd plus iovec ranges and advice values passed to `process_madvise()`.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/mman.h`, `tst_test.h`, `lapi/mmap.h`, `lapi/syscalls.h`, `process_madvise.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TST_CHECKPOINT_WAIT`, `TST_CHECKPOINT_WAKE`, `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_EXP_EXPR`, `TST_KB`, `TST_MB`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/process_madvise/process_madvise01.c -->
