<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.h -->
## sources/test-tools/liburing/test/helpers.h

Purpose: public helper declarations and shared test result/setup constants for the liburing test suite.

Important APIs/types/functions: enums `t_setup_ret` and `t_test_result`, declarations for allocation/file/socket/ring helpers, `t_probe_defer_taskrun`, nonblocking helpers, `__io_uring_flush_sq`, timing helpers, `t_submit_and_wait_single`, iovec utilities, and inline `t_io_uring_init_sqarray`.

Control flow: header-only logic is limited to `t_io_uring_init_sqarray`, which calls `__io_uring_queue_init_params` with no SQ array memory and converts nonnegative returns to zero.

State and persistence behavior: no persistent state. It defines shared return-code contracts: pass `0`, fail `1`, skip `77`, and setup skip vs OK.

Dependencies and integration points: includes `liburing.h`, internal `setup.h`, socket/time/system headers, and exposes helpers to C and C++ callers with `extern "C"`.

Risks: changes here affect nearly every test. The inline setup wrapper reaches into internal liburing setup APIs.

Test signals: successful compilation and broad dependent test execution validate the declarations and result constants.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/helpers.h -->
