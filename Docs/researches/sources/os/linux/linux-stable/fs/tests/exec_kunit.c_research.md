# File Research: sources/os/linux/linux-stable/fs/tests/exec_kunit.c

Purpose: KUnit tests for exec argument/environment stack-limit calculation.

Key responsibilities:
- Defines table-driven cases for `bprm_stack_limits()`.
- Covers negative `argc`/`envc`, maximum string counts, pointer-count overflow-style inputs, zero stack limits, `ARG_MAX` boundaries, and `_STK_LIM` clamping.
- Verifies expected return codes and, under MMU builds, expected `bprm.argmin`.

Important interactions:
- Tests `struct linux_binprm` fields consumed by exec setup.
- Uses KUnit expectations and suite registration named `exec`.

Notable invariants and risks:
- The tests encode important boundary assumptions: `ARG_MAX == 32 * SZ_4K`, `_STK_LIM == SZ_8M`, and `MAX_ARG_STRINGS == 0x7fffffff`.
