# File Research: sources/os/plan9/plan9/sys/src/cmd/qc/txt.c

Main PowerPC code-generation backend for the Plan 9 C compiler.

Key responsibilities:
- Initializes target identity, register reservations, pseudo nodes, string/rathole symbols, and 64-bit support.
- Finalizes output by checking register leaks, flushing strings, emitting globals, and writing object code.
- Allocates/free integer, floating-point, 64-bit register-pair, argument, and stack temporary nodes.
- Converts AST nodes to `Adr` operands.
- Implements `gmove()` for scalar, floating, memory, constant, and 64-bit moves/conversions.
- Emits instructions with two-, three-, and four-operand helper forms.
- Maps generic compiler operations to PowerPC opcodes.
- Implements 64-bit arithmetic/logical/shift/multiply lowering using register pairs.
- Emits branches, patches branch targets, emits pseudo ops, checks immediate ranges, allocates external registers, and defines type width/cast tables.

Dependencies:
- Depends on `gc.h`, `q.out.h`, `swt.c` alignment/output helpers, `com64` support, register conventions, and PowerPC opcode names.

Notable risks:
- Many ABI details are hardcoded: return registers, stack argument layout, R0 zero behavior, and fixed floating constants.
- Floating/integer conversions use rathole stack temporaries and simplified sequences.
- 64-bit operations are synthesized manually and are sensitive to high/low word ordering.
