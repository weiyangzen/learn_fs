# File Research: sources/os/plan9/plan9/sys/src/cmd/6c/list.c

This file implements formatted printing for amd64 compiler backend objects. `listinit` installs format handlers for opcodes, operands, programs, registers, symbols, and bitsets.

`Pconv` renders `Prog` instructions, with special cases for `DATA` and `TEXT` pseudo-ops. `Aconv` maps opcode enum values through `anames`. `Dconv` formats amd64 operands including indirect addressing, branches, extern/static/auto/param symbols, constants, floating constants, string constants, and address constants. `Rconv` maps register numbers to printable register names. `Sconv` escapes 8-byte string constants. `Bconv` renders live-variable bitsets by symbol/offset.

This is not code generation itself, but it is essential for compiler diagnostics, debug modes, and register allocator tracing.

Filesystem relevance is build observability: when filesystem-related C code miscompiles or triggers backend diagnostics, these formatters make emitted instructions and operands understandable.
