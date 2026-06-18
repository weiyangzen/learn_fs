# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ktest.h

## Purpose
Defines the ktest userspace ioctl ABI and the kernel module test registration/result API hidden behind `_KERNEL`.

## Main Interfaces
- Naming and serialization constants:
  - `KTEST_SEPARATOR`
  - `KTEST_DEF_TRIPLE`
  - `KTEST_MAX_NAME_LEN`
  - `KTEST_MAX_TRIPLE_LEN`
  - `KTEST_MAX_LOG_LEN`
  - nvlist key strings
  - `KTEST_SER_FMT_VSN`
- Safety limit:
  - `KTEST_IOCTL_MAX_LEN`
- Ioctls:
  - `KTEST_IOCTL_RUN_TEST`
  - `KTEST_IOCTL_LIST_TESTS`
- Enums:
  - `ktest_test_flags_t`
  - `ktest_result_type_t`
- ABI structures:
  - `ktest_result_t`
  - `ktest_run_op_t`
  - `ktest_list_op_t`
- Kernel-only opaque handles:
  - `ktest_module_hdl_t`
  - `ktest_suite_hdl_t`
  - `ktest_test_hdl_t`
  - `ktest_ctx_hdl_t`
- Kernel module API:
  - module/suite/test creation and registration
  - module hold/release and symbol lookup helpers
  - input retrieval
  - result and message helpers
- Test macros:
  - `KT_PASS`, `KT_FAIL`, `KT_ERROR`, `KT_SKIP`
  - assertion macros for signed, unsigned, pointer, boolean, and zero checks
  - goto variants
  - error-result assertion variants

## Dependencies And Relationships
Includes DDI, module-control, param, and type headers. The header explicitly owns both ioctl ABI and in-kernel ktest module ABI.

## Research Notes
Assertion macros record source line numbers and return or jump on failure. The distinction between fail and error is encoded in separate result helpers and macro families. Input-bearing tests are marked with `KTEST_FLAG_INPUT`.
