<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/pkey01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/pkey01.c

Purpose: Memory Protection Keys for Userspace (PKU aka PKEYs) is a Skylake-SP server feature that provides a mechanism for enforcing page-based protections, but without requiring modification of the page tables when an application changes protection domains. It works by dedicating 4 previously ignored bits in each page table entry to a "protection key", giving 16 possible keys. Basic method for PKEYs testing: 1. test allocates a pkey(e.g. PKEY_DISABLE_ACCESS) via pkey_alloc() 2. pkey_mprotect() apply this pkey to a piece of memory(buffer) 3. check if access right of the buffer has been changed and take effect 4. remove th

Important APIs/types/functions: includes `stdio.h`, `unistd.h`, `errno.h`, `stdlib.h`, `sys/syscall.h`, `sys/mman.h`, `sys/wait.h`, `lapi/pkey.h`; exercises `pkey_alloc`, `pkey_free`, `pkey_mprotect`, `read`, `write`; defines `setup`, `__attribute__`, `pkey_test`, `verify_pkey`; uses flags/constants `O_CREAT`, `O_RDWR`, `PKEY_DISABLE_ACCESS`, `PKEY_DISABLE_EXECUTE`, `PKEY_DISABLE_WRITE`.

Control flow centers on `setup`, `__attribute__`, `pkey_test`, `verify_pkey`. The `struct tst_test` registration wires `.tcnt`, `.needs_root`, `.needs_tmpdir`, `.forks_child`, `.test`, `.setup`, `.hugepages` into the LTP runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is allocated protection keys, PKRU-enforced permissions, mmap-backed buffers, optional huge pages, and forked children used to provoke SIGSEGV safely.

Dependencies and integration points: Depends on `lapi/pkey.h`, x86/architecture PKU support, root privileges, optional huge pages, mmap/mprotect, and forked SIGSEGV probes. Direct include dependencies include `stdio.h`, `unistd.h`, `errno.h`, `stdlib.h`, `sys/syscall.h`, `sys/mman.h`.

Risks and test signals: PKU behavior is architecture-specific and deliberately causes SIGSEGV in children; execute-disable and huge-page cases may be unsupported. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_REQUEST`; checks errno values `EINVAL`; uses child exit/wait status as part of the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pkeys/pkey01.c -->
