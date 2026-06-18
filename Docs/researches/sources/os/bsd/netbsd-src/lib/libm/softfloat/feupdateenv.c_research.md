# File Research: sources/os/bsd/netbsd-src/lib/libm/softfloat/feupdateenv.c

Implements `feupdateenv`.

Key behavior:
- Saves current exception flags.
- Restores rounding mode and exception mask from the supplied environment.
- Raises the previously saved exception flags with `feraiseexcept`.

Notable risk:
- The code sets sticky flags from `__FENV_GET_MASK(envp)` rather than `__FENV_GET_FLAGS(envp)`, which is surprising for an environment restore path and may be intentional only if the fenv layout macros encode differently.
