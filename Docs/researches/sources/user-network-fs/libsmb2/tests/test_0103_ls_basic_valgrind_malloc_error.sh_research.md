<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0103_ls_basic_valgrind_malloc_error.sh -->
# sources/user-network-fs/libsmb2/tests/test_0103_ls_basic_valgrind_malloc_error.sh

Purpose: Malloc/calloc failure-injection test for `prog_ls`.

Important APIs, types, and functions: Uses ltrace to count allocation calls, then loops `MALLOC_FAIL` and `CALLOC_FAIL` indices under valgrind with error exit code 77.

Control flow: It runs `prog_ls` repeatedly while the program's interposed allocation wrappers fail one allocation site at a time.

State and persistence behavior: No remote mutation beyond listing. Process-local environment controls injected allocation failures.

Dependencies and integration points: Depends on ltrace, valgrind, libtool, and the allocation interposition in `prog_ls.c`.

Risks: Ltrace output format and allocator behavior vary by platform. It accepts many command failures, so it mainly catches crashes/leaks rather than semantic success.

Test signals: Memory-failure robustness signal for directory listing path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/tests/test_0103_ls_basic_valgrind_malloc_error.sh -->
