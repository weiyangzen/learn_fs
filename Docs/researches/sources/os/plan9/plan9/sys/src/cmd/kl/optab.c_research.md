# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/optab.c

Read fully: 199 lines, 7369 bytes. SHA-256 prefix: `53cca30ee5ca727a`.

This file is the SPARC linker’s instruction-selection table. `optab[]` maps abstract opcodes and operand classes to an `asmout()` type, emitted byte size, and optional base register parameter.

The table covers pseudo-ops, moves, immediate constants, short and long memory references, ASI loads/stores, processor register moves, byte/halfword extension moves, arithmetic/logical ops, compare variants, jumps/calls/branches/traps, floating-point loads/stores/ops, word literals, division/modulus synthetic sequences, and annulable conditional branches.

Integration: `span.c` sorts and indexes this table in `buildop()`, `oplook()` caches matching rows in each `Prog`, and `asm.c` interprets `type` values to emit actual SPARC words.

Risk notes: the numeric `type` values are an implicit contract with the large `asmout()` switch. Any table edit must keep size/type/operand-class semantics consistent.
