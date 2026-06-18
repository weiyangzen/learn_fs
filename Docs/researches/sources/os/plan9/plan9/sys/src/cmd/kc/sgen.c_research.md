# File Research: sources/os/plan9/plan9/sys/src/cmd/kc/sgen.c

This file provides simple generation helpers, especially AST addressability and complexity analysis via `xcom()`.

`noretval()` emits dummy uses of return registers when a function has no return value but the compiler needs to model register clobbering. `xcom()` classifies nodes as constants, names, registers, indirect registers, address expressions, indirections, and constant-offset additions.

`xcom()` also rewrites optimizable arithmetic: multiplication by a power of two becomes shift left, unsigned division by a power of two becomes logical shift right, and modulo by a power of two becomes bitwise and. It canonicalizes constants to the right side for comparisons and commutative integer ops.

This file feeds `cgen.c`: its `addable` and `complex` values determine whether expressions can be emitted directly, need registers, or require function-call-safe temporaries.
