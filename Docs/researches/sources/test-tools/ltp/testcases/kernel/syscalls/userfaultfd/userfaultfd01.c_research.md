<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd01.c

Purpose: Force a pagefault event and handle it using :manpage:`userfaultfd(2)` from a different thread.

Important APIs/types/functions: includes `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`; exercises `userfaultfd`; defines `setup`, `set_pages`, `reset_pages`, `run`; uses constants `MAP_ANONYMOUS`, `MAP_PRIVATE`, `O_CLOEXEC`, `O_NONBLOCK`, `PROT_READ`, `PROT_WRITE`, `UFFDIO_API`, `UFFDIO_COPY`, `UFFDIO_REGISTER`, `UFFDIO_REGISTER_MODE_MISSING`, `UFFD_API`, `UFFD_EVENT`, `UFFD_EVENT_PAGEFAULT`, `UFFD_USER_MODE_ONLY`.

Control flow centers on `setup`, `set_pages`, `reset_pages`, `run`. The `struct tst_test` registration wires `.setup`, `.test`, `.tcnt`, `.cleanup` into the runner.

State and persistence behavior: Runtime state is anonymous or shmem mappings registered with userfaultfd, fault events read by handler threads, and UFFD ioctl state.

Dependencies and integration points: Depends on `lapi/userfaultfd.h`, `SAFE_USERFAULTFD`, pthread helpers, mmap/memfd support, and feature probes for MOVE, ZEROPAGE, WP, POISON, MINOR_SHMEM, or `/dev/userfaultfd`. Direct include dependencies include `poll.h`, `tst_test.h`, `tst_safe_macros.h`, `tst_safe_pthread.h`, `lapi/userfaultfd.h`.

Risks and test signals: Userfaultfd is gated by kernel config, sysctl, features, and permissions; handler-thread races can deadlock if events or ioctls are mishandled. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TPASS`; uses child/thread synchronization as part of the assertion.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/userfaultfd/userfaultfd01.c -->
