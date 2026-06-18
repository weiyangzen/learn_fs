# sources/test-tools/strace/src/linux/tile/syscallent.h

## Purpose
Defines Tile native personality syscall table entries by including the generic 64-bit syscall table and appending Tile architecture-specific calls.

## Important APIs, Types, and Functions
Includes `../64/syscallent.h`, then adds entries `[244] cmpxchg_badaddr` and `[245] cacheflush` using `SEN(printargs)`. These rows are initializer data for `struct_sysent`.

## Control Flow and Integration
No runtime control flow. The include produces the base 64-bit table, and the local rows override/fill the architecture-specific range `[244 ... 259]`.

## State and Persistence
No local mutable state. The compiled static table drives syscall decoding for Tile personality 0.

## Dependencies
Depends on generic 64-bit syscall table numbering, `SEN` and flag macros, and Tile personality selection in `get_scno.c`.

## Risks
The arch-specific slots use `printargs`, so decoding is intentionally generic. Incorrect placement would collide with generic syscall numbers or leave Tile-specific calls unknown.

## Test Signals
Native Tile traces for syscall numbers 244 and 245 should print `cmpxchg_badaddr` and `cacheflush`. Generic 64-bit syscalls should still decode through the included table.
