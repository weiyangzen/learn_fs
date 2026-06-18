# File Research: sources/os/plan9/plan9/sys/src/cmd/5i/float.c

## Scope

Placeholder floating-point/cop1 dispatch support for `5i`.

## Behavior

- Defines a table of floating operations and trap helpers.
- Most operation handlers are empty stubs: arithmetic, moves, conversions, load/store, branches, and comparisons do not emulate FP effects.
- `unimp()`, `inval()`, and `ifmt()` report faults and longjmp back to the debugger.

## Dependencies

Uses `arm.h`, `bioout`, and `errjmp`.

## Risks And Invariants

- Floating-point emulation is effectively incomplete; programs depending on FP instructions will run incorrectly unless they trap through unimplemented paths.
- The `cop1` naming is MIPS-like legacy terminology in an ARM emulator source tree.
