# sources/test-tools/kdevops/scripts/kconfig/lkc_proto.h

## Purpose
`lkc_proto.h` provides forward declarations for Kconfig persistence, symbol, property, and expression functions used across compilation units.

## Important APIs, Types, And Functions
It declares config I/O functions from `confdata.c`, symbol lookup/search/type/value functions from `symbol.c`, property type naming, and `expr_print()` from `expr.c`.

## Control Flow
There is no runtime flow; it is a prototype surface.

## State And Persistence
The declared config functions read and write persistent configuration files. The header itself has no state.

## Dependencies And Integration Points
It is included by `lkc.h` after standard variadic support. It keeps compiler checking consistent across Kconfig modules.

## Risks And Test Signals
Prototype drift causes build failures or worse if declarations stop matching definitions. Full `make conf mconf nconf` is the primary signal, plus warnings with strict prototype flags.
