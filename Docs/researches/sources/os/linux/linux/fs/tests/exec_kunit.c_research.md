# File Research: sources/os/linux/linux/fs/tests/exec_kunit.c

Purpose: KUnit coverage for `bprm_stack_limits()` argument/environment stack accounting.

Test coverage:
- Negative `argc`/`envc` and counts at/above `MAX_ARG_STRINGS` return `-E2BIG`.
- Includes overflow-oriented 32-bit-sensitive argument count cases.
- Under `CONFIG_MMU`, verifies pathological low `bprm->p` is rejected.
- Tests `rlim_stack` clamping to at least `ARG_MAX`, upper cap at `_STK_LIM / 4 * 3`, pointer accounting, and argc minimum of one.
- Confirms expected constants: `_STK_LIM == SZ_8M`, `ARG_MAX == 32 * SZ_4K`, `MAX_ARG_STRINGS == 0x7FFFFFFF`.

Structure:
- Test data table of `linux_binprm` inputs and expected return/argmin.
- Single test case `exec_test_bprm_stack_limits`.
- KUnit suite name is `"exec"`.
