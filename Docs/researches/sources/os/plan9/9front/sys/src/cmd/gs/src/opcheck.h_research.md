# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/opcheck.h

## Purpose
Macro utilities for Ghostscript PostScript operator operand validation.

## Main Structure
- Defines type checks: `check_type_only`, `check_stype_only`, array checks, procedure checks.
- Defines access checks: read, write, execute, and combined type/access checks.
- Defines unsigned integer bound checks: `check_int_leu`, `check_int_leu_only`, `check_int_ltu`.
- Declares `check_proc_failed`.

## Integration Notes
- Requires allocation/reference/error context headers such as `ialloc.h`, `iref.h`, and `ierrors.h`.
- Used by operator implementations to return PostScript errors such as `e_typecheck`, `e_invalidaccess`, and `e_rangecheck`.

## Risks and Edge Cases
- Macros assume surrounding code has `return_error`, `BEGIN`, `END`, and reference helpers in scope.
- Some macros evaluate ref arguments multiple times or require lvalue-like `ref` expressions.
