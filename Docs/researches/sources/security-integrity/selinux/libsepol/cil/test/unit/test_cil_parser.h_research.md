# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_parser.h

## Purpose
This header declares the parser smoke test for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `test_cil_parser(CuTest *)`.

## Control Flow
There is no executable logic. `CilTest.c` registers the declaration, and the implementation calls `cil_parser` on fixture policy data.

## State And Persistence
No state is stored. It provides a prototype only.

## Dependencies And Integration Points
The header integrates `test_cil_parser.c` with the shared test runner and indirectly with parser internals.

## Risks
Only one parser test is exposed, so parser coverage depends heavily on build-AST tests that construct parse trees manually rather than exercising parser text input.

## Test Signals
The header signals a single parser acceptance test.
