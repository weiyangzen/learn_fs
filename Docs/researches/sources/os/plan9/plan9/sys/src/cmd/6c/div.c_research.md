# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/div.c

This file implements optimized division and modulo by invariant integer constants for amd64 code generation. It is based on Granlund and Montgomery’s multiplication-based division method.

`multiplier`, `sdiv`, and `udiv` compute magic multipliers, shifts, and adjustment flags for signed and unsigned 32-bit division. `sdivgen` and `udivgen` emit instruction sequences using multiply, shifts, adjustment adds, and sign correction instead of hardware divide when the divisor is constant.

`sdiv2` and `smod2` handle signed division and modulo by powers of two, preserving C signed-division semantics through sign extension and biasing before arithmetic shifts. `sext` produces sign-extension helpers, using `CDQ` when possible.

This is performance-sensitive compiler infrastructure. It matters to filesystem code indirectly because hot paths compiled with `6c`, including block and metadata arithmetic, benefit from constant division lowering without requiring source-level changes.
