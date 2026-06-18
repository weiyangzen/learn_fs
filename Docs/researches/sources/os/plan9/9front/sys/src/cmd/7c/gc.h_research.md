# File Research: sources/os/plan9/9front/sys/src/cmd/7c/gc.h

Primary ARM64 backend header for `7c`. It includes common compiler definitions and `7.out.h`, defines target C type sizes, core backend structs, globals, register-allocation bitset macros, pass constants, and function prototypes across the backend files.

Key contents:
- Target data model: `char=1`, `short=2`, `int=4`, `long=4`, pointer/vlong/double `=8`, float `=4`.
- Defines `Adr`, `Prog`, `Case`, `C1`, `Multab`, `Hintab`, `Var`, `Reg`, and `Rgn`.
- `Prog` carries `from`, optional `from3`, `to`, opcode, register field, source line, and link pointer.
- `Reg` is the optimizer CFG node with use/set bitsets, liveness/synchrony bitsets, predecessor/successor links, loop weight, and attached `Prog`.
- Global state includes instruction list pointers, current PC, switch cases, constant nodes, register-use counters, string literal buffers, external register offsets, register optimizer variables, and variable tables.
- Declares all cross-file backend entry points for generation, emission, switch handling, listing, register optimization, and peephole optimization.
- Installs `#pragma varargck` format contracts for Plan 9 custom formatters such as `%A`, `%P`, `%D`, `%B`.

Filesystem relevance: indirect; it is the backend contract binding the 9front ARM64 compiler.
