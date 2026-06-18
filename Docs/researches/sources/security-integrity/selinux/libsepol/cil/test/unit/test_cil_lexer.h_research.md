# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.h

## Purpose
This header declares the lexer unit tests for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `test_cil_lexer_setup(CuTest *)` and `test_cil_lexer_next(CuTest *)`.

## Control Flow
There is no runtime control flow. The declarations are consumed by `CilTest.c`, which registers the functions into the unit test suite.

## State And Persistence
No state or persistence behavior is present. It only provides function prototypes.

## Dependencies And Integration Points
The header links the lexer implementation tests to the common CIL test harness. The implementation integrates with `cil_lexer_setup`, `cil_lexer_next`, and token definitions from `cil_lexer.h`.

## Risks
The small declaration set mirrors the narrow lexer coverage. Additional lexer edge cases require adding new declarations and suite registration.

## Test Signals
The intended lexer test surface covers setup and sequential next-token behavior.
