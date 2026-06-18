<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd02.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread using UFFDIO_MOVE.

Important APIs/types/functions: includes `config.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `userfaultfd`; defines `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_MOVE`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MISSING`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`, `_SC_PAGE_SIZE`.

Control flow centers on `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.test_all`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `config.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd02.c -->
