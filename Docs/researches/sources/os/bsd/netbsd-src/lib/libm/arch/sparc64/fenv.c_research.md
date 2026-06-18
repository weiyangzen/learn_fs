# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/sparc64/fenv.c

## Scope

Implements the C99 floating-point environment API for SPARC/SPARC64 by directly loading and storing the SPARC floating-point state register (`%fsr`). It provides exception flag, rounding mode, environment save/restore, and NetBSD exception-mask extension functions.

## APIs And Behavior

- Defines weak aliases for standard and internal `_fe*` symbols.
- Uses `ldx/stx %fsr` on 64-bit SPARC and `ld/st %fsr` on non-`__arch64__` builds.
- `feclearexcept`, `fegetexceptflag`, `fesetexceptflag`, and `fetestexcept` operate on `FE_ALL_EXCEPT` bits in the saved FSR.
- `feraiseexcept` raises exceptions through volatile floating-point operations for invalid, divide-by-zero, overflow, underflow, and inexact.
- `fegetround` / `fesetround` read and update rounding bits at `_ROUND_SHIFT`.
- `fegetenv`, `feholdexcept`, `fesetenv`, and `feupdateenv` save/restore the FSR and replay saved exceptions.
- `feenableexcept`, `fedisableexcept`, and `fegetexcept` manipulate the enabled-exception mask via `_FPUSW_SHIFT` / `_ENABLE_MASK`.

## Dependencies And Risks

- Depends on `<fenv.h>` architecture bit definitions matching SPARC FSR layout.
- `feraiseexcept` relies on volatile arithmetic to defeat compiler constant folding.
- Environment restore is a raw FSR load; callers must pass a valid `fenv_t` or a valid environment macro.
