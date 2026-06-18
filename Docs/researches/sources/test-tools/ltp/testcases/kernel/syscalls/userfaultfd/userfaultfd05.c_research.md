<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd05.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread testing UFFDIO_WRITEPROTECT_MODE_WP. While the WP fault is pending, the write must NOT be visible. Resolve the fault by clearing WP so the writer can resume.

Important APIs/types/functions: includes `config.h`, `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `userfaultfd`, `write`; defines `setup`, `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `O_NONBLOCK`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_WP`, `UFFDIO_WRITEPROTECT`, `UFFDIO_WRITEPROTECT_MODE_WP`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`.

Control flow centers on `setup`, `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.setup`, `.test_all`, `.needs_kconfigs`, `.cleanup` into the runner. Named case hints include `CONFIG_HAVE_ARCH_USERFAULTFD_WP=y`.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd05.c -->
