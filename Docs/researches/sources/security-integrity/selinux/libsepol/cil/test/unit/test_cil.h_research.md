# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil.h

## Purpose
`test_cil.h` declares the core CIL unit test functions implemented in `test_cil.c` so the suite registry can add them.

## Important APIs, Types, And Functions
The header declares CuTest-style functions for symbol table array initialization, database initialization, positive `cil_get_symtab()` lookup paths, and negative `cil_get_symtab()` inputs. It also declares `test_cil_symtab_array_init_null_symtab_neg(CuTest *)`, which is not implemented in the paired `test_cil.c` in this subset and is not registered in `CilTest.c`.

## Control Flow
There is no executable flow. The prototypes are consumed by `CilTest.c` at compile time for suite registration and by the compiler for function type checking.

## State And Persistence
No state is stored in this header. Test state is owned by the implementations.

## Dependencies And Integration Points
It includes `CuTest.h` for the `CuTest` type. It integrates `test_cil.c` with the central suite factory in `CilTest.c`.

## Risks
The stale-looking declaration for `test_cil_symtab_array_init_null_symtab_neg()` can mislead maintainers or cause link errors if registered without an implementation. The header has no include of CIL internals because all test functions expose only the CuTest signature.

## Test Signals
Presence of these prototypes indicates that core CIL initialization and symbol-table lookup tests are intended to be part of the base suite.
