# File Research: sources/os/plan9/9front/sys/src/cmd/qa/a.h

Shared header for the `qa` assembler frontend, a Plan 9-style assembler targeting the architecture described by `../qc/q.out.h` with PowerPC-like registers/instructions. It defines symbol, input, address, and history structures plus global parser/lexer/output state.

Key contents:
- Constants for symbol table, include depth, IO buffers, macro state, hash size, and string sizes.
- `Sym`, `Io`, `Gen`, and `Hist` model symbols/macros, stacked input, generic operands, and file history.
- Global declarations include symbol hash, include paths, IO stacks, pc/pass state, output buffer, and assembler flags.
- Prototypes cover lexical input, macro handling, parser, symbol setup, output encoding, history emission, and top-level assembly.

Integration points:
- Included by `a.y` and companion assembler implementation files in `qa`.
- Depends on generated/architecture constants from `../qc/q.out.h`.

Risks:
- Heavy use of globals and `EXTERN` convention mirrors old Plan 9 compiler code.
- Fixed buffer/include/macro limits constrain accepted assembly.
