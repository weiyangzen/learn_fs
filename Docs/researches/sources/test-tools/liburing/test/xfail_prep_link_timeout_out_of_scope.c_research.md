# sources/test-tools/liburing/test/xfail_prep_link_timeout_out_of_scope.c

Purpose: negative ASan-oriented test for stack lifetime misuse with timeout preparation. It intentionally passes a stack `__kernel_timespec` to a timeout SQE and lets the variable go out of scope before submit.

Important APIs/types/functions: `io_uring_queue_init`, `io_uring_get_sqe`, `io_uring_prep_timeout`, `io_uring_sqe_set_data`, and `io_uring_submit_and_wait`.

Control flow: main skips when invoked with arguments. It initializes a ring; if queue init fails it returns pass because this xfail expects inverted handling. Inside a nested scope it initializes `timespec`, prepares a timeout SQE using its address, sets user data, leaves scope, then submits and waits. It always returns `T_EXIT_PASS`.

State/persistence behavior: no persistent state. The test intentionally creates invalid pointer lifetime state in user memory.

Dependencies/integration: designed for sanitizer runs, particularly AddressSanitizer, to catch stack-use-after-scope in liburing prep/submit paths.

Risks/test signals: by normal exit code this file is not a conventional correctness test; the expected interesting signal is an ASan report. Without sanitizer it may appear to pass despite the misuse.
