# sources/security-integrity/selinux/libsemanage/tests/utilities.h

## Purpose
`utilities.h` is the shared test support header for libsemanage CUnit suites. It exposes the global handle, common fixture lifecycle functions, and assertion helpers used across object-specific tests.

## Important APIs, Types, and Functions
The header includes standard C/POSIX headers, CUnit, and `semanage/semanage.h`. It defines `CU_ASSERT_CONTEXT_EQUAL`, index constants `I_NULL`, `I_FIRST`, `I_SECOND`, and `I_THIRD`, the global `extern semanage_handle_t *sh`, and `level_t` with states `SH_NULL`, `SH_HANDLE`, `SH_CONNECT`, and `SH_TRANS`.

It declares `test_msg_handler`, handle setup/cleanup helpers, individual helper actions, and test-store functions: `create_test_store`, `write_test_policy_from_file`, `write_test_policy_src`, `destroy_test_store`, `enable_test_store`, and `disable_test_store`.

## Control Flow
The header has no runtime flow, but its `CU_ASSERT_CONTEXT_EQUAL` macro performs context serialization through `semanage_context_to_string`, compares the resulting strings, and frees both buffers. Under `__CHECKER__`, it overrides selected fatal CUnit macros to also call `assert`, improving static-analysis understanding.

## State and Persistence Behavior
The header exposes the process-global handle and the `level_t` lifecycle contract used by `setup_handle` and `cleanup_handle`. Persistence behavior is implemented in `utilities.c`.

## Dependencies and Integration Points
It is included by all libsemanage tests in this subset. It couples tests to CUnit and the libsemanage public handle/context APIs.

## Risks and Test Signals
`CU_ASSERT_CONTEXT_EQUAL` assumes both context-to-string calls succeed and that `sh` is a valid global handle. Macro arguments are evaluated inside the macro and should be side-effect free. The meaningful test signal is broad compile-time and runtime reuse across suites.
