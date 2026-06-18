# File Research: sources/os/plan9/plan9/sys/src/cmd/kl/l.h

Read fully: 330 lines, 5406 bytes. SHA-256 prefix: `16ad6b39ab26511e`.

This is the central private header for the SPARC linker. It defines the core IR structures `Adr`, `Prog`, `Sym`, `Auto`, and `Optab`; operand classes; symbol types; scheduler mark flags; global linker state; and function prototypes.

Key structures:
- `Adr`: instruction operand, with offset/string/IEEE payload, symbol/auto link, type, register, name, and cached class.
- `Prog`: instruction node with `from`, `to`, branch/linear links, PC, register-use metadata, line, mark flags, optab cache, opcode, and auxiliary register.
- `Sym`: linker symbol with name, type, version, become/frame metadata, value, and hash link.
- `Optab`: instruction-selection table row used by `oplook()` and `asmout()`.

It also declares all shared globals: text/data lists, symbol hash, output buffers, debug flags, endian tables, header/layout constants, profiling helper program pointers, and scheduling/assembly state.

Integration: every `kl/*.c` file includes this header. It is the contract between object loading, patching, data layout, scheduling, span, and assembly.

Risk notes: this codebase relies on global mutable state and cached operand classes. Any mutation of `Adr` operands after classification must clear or recompute class fields.
