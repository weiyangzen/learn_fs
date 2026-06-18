# sources/test-tools/liburing/test/test.h

Purpose: shared test configuration header defining common io_uring setup flag combinations for tests that iterate over ring modes.

Important APIs/types/functions: `io_uring_test_config`, `io_uring_test_configs`, `FOR_ALL_TEST_CONFIGS`, `IORING_GET_TEST_CONFIG_FLAGS()`, `IORING_GET_TEST_CONFIG_DESCRIPTION()`, and setup flags `IORING_SETUP_SQE128`, `IORING_SETUP_CQE32`, and `IORING_SETUP_SQ_REWIND`.

Control flow: no runtime control flow beyond macro expansion. Consumers use `FOR_ALL_TEST_CONFIGS` to iterate the static array and retrieve flags/descriptions by loop index `i`.

State/persistence behavior: contains a static header-local array marked unused to avoid compiler warnings. No mutable persistent state.

Dependencies/integration: depends on liburing setup flag definitions being visible before inclusion. The `extern "C"` guard supports C++ tests.

Risks/test signals: macro design assumes the caller's loop variable is named `i`; misuse outside the provided loop macro can break compilation or read the wrong entry.
