# sources/test-tools/liburing/test/nop.c

Purpose: baseline NOP stress test across all configured ring test modes, including async requests, drain barriers, injected results, and optional CQE32 verification.

Important APIs/types/functions: `FOR_ALL_TEST_CONFIGS`, `IORING_GET_TEST_CONFIG_FLAGS`, `io_uring_prep_nop`, `IOSQE_ASYNC`, `IOSQE_IO_DRAIN`, `IORING_NOP_INJECT_RESULT`, `IORING_SETUP_CQE32`, and `cqe->big_cqe`.

Control flow: for each test configuration, `test_ring()` loops 1000 times, alternating async flag use. Each iteration submits one NOP, an eight-NOP batch with the fifth marked drain, and an injected-result NOP expecting either `-EFAULT` or `-EINVAL`.

State and persistence behavior: `seq` provides increasing `user_data`; otherwise only ring CQ/SQ state is used. No persistent state.

Dependencies and integration points: depends on `test.h` configuration macros and liburing support for each selected setup flag.

Risks and test signals: failures are missing `user_data`, nonzero CQE32 extras for ordinary NOPs, bad drain batch submission, or injected-result handling outside allowed error codes.
