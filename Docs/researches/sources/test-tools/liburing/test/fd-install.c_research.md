<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/fd-install.c -->
## sources/test-tools/liburing/test/fd-install.c

Purpose: tests installing fixed/direct descriptors from a ring's fixed-file table into the regular process fd table.

Important APIs/types/functions: `test_flags`, `test_linked`, `test_not_fixed`, `test_creds`, `test_ring_exit`, `io_uring_prep_fixed_fd_install`, `io_uring_register_files`, `IORING_FIXED_FD_NO_CLOEXEC`, `IOSQE_FIXED_FILE`, `IOSQE_ASYNC`, and linked SQEs.

Control flow: scenarios register pipe fds as fixed files, verify invalid install flags return `-EINVAL`, verify accepted flags produce a real fd, check linked NOP+install completion, check install without fixed-file context, and run variants with async execution and ring teardown interactions.

State and persistence behavior: registered file tables hold references to pipe fds while install operations create ordinary process fds that must be closed separately. The global `no_fd_install` records unsupported kernel behavior.

Dependencies and integration points: integrates fixed-file registration with fd allocation, close-on-exec flag handling, linked SQEs, credentials, and ring lifetime.

Risks: fd leaks on early failure are the main local risk. Kernel support is feature-dependent and may skip on `-EINVAL`.

Test signals: pass means direct descriptors can be safely materialized as normal fds and invalid flag/fixedness combinations fail as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/fd-install.c -->
