# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/x86_64/fenv.c

## Scope

Implements C99 floating-point environment functions for x86_64 by coordinating x87 environment/control/status state and SSE MXCSR state.

## APIs And Behavior

- Defines weak aliases for standard `fenv.h` functions.
- Provides inline assembly wrappers for `fldcw`, `fnstcw`, `fnstsw`, `fnclex`, `fldenv`, `fnstenv`, `fwait`, `ldmxcsr`, and `stmxcsr`.
- Defines `__fe_dfl_env` and a constructor that captures runtime x87 reserved/control bits for the default environment.
- Exception functions clear, test, get, set, and raise flags across both x87 and MXCSR. `feraiseexcept` sets flags and executes `fwait`.
- Rounding functions require x87 and SSE rounding modes to agree; `fegetround` returns `-1` if they differ.
- `fegetenv` repairs the x87 control word after `fnstenv`, because `fnstenv` masks/clears pending state.
- `fesetenv` and `feupdateenv` preserve reserved high bits from the live x87 environment when applying `FE_DFL_ENV`.
- `feenableexcept`, `fedisableexcept`, and `fegetexcept` convert between x87/SSE mask semantics and enabled-exception reporting.

## Dependencies And Risks

- Requires `<fenv.h>` x87/MXCSR bit masks to match hardware layout.
- x87 exception masks are inverted relative to enable semantics; the code carefully returns enabled masks as `FE_ALL_EXCEPT & ~omask`.
- `fnstenv` side effects are subtle and explicitly compensated.
