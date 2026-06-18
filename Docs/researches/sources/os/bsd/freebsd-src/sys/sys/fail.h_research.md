# File Research: sources/os/bsd/freebsd-src/sys/sys/fail.h

## Purpose
Defines the kernel failpoint facility used for sysctl-controlled fault injection in tests and debugging.

## Main Interfaces
- Return codes: `FAIL_POINT_RC_CONTINUE`, `RETURN`, `QUEUED`.
- `struct fail_point`: name, source location, refcount, current setting, flags, sleep callbacks, callout.
- Flags:
  - `FAIL_POINT_DYNAMIC_NAME`
  - `FAIL_POINT_USE_TIMEOUT_PATH`
  - `FAIL_POINT_NONSLEEPABLE`
- Fast-path macro: `FAIL_POINT_IS_OFF`.
- APIs:
  - `fail_point_init`
  - `fail_point_is_off`
  - `fail_point_alloc_callout`
  - `fail_point_use_timeout_path`
  - `fail_point_destroy`
  - `fail_point_eval`
  - `fail_point_eval_nontrivial`
  - sysctl handlers in kernel builds
- Sleep callback setters for pre/post sleep hooks.
- Definition/evaluation macros:
  - `KFAIL_POINT_DEFINE`, `KFAIL_POINT_DECLARE`
  - `KFAIL_POINT_RETURN`
  - `KFAIL_POINT_RETURN_VOID`
  - `KFAIL_POINT_ERROR`
  - `KFAIL_POINT_GOTO`
  - `KFAIL_POINT_SLEEP_CALLBACKS`
  - `KFAIL_POINT_CODE`, `KFAIL_POINT_CODE_FLAGS`, `KFAIL_POINT_CODE_COND`
- Sysctl root declaration: `_debug_fail_point`, alias `DEBUG_FP`.

## Dependencies And Integration
Uses sysctl, callouts, locks, condition variables, linker sets, and kernel system headers. Failpoints become sysctl nodes with status nodes.

## Implementation Notes
`fail_point_eval` is inline and returns immediately when `fp_setting == NULL`, preserving near-zero disabled overhead. Nontrivial parsing and actions live outside the header.

## Risk Notes
Macro-generated local `RETURN_VALUE` can collide with surrounding code expectations. Sleep/timeout mode requires valid post-sleep callbacks. Failpoint state lifetime is protected by `fp_ref_cnt` and must remain synchronized with implementation.
