# File Research: sources/os/plan9/9front/sys/src/cmd/7l/l.h

Central header for the 9front ARM64 linker `7l`.

Major definitions:
- `Adr`: instruction operand/address form, including offsets, strings, IEEE constants, symbols, registers, names, and operand class.
- `Prog`: linker instruction node with `from`, optional `from3`, `to`, branch target, PC, line, marks, opcode, and cached optab index.
- `Sym`: linker symbol table entry with type, version, value, signature, file index, frame/become metadata, and linkage.
- `Autom`: automatic/local symbol metadata attached to text symbols.
- `Optab`: instruction pattern entry used by the encoder, with opcode, operand classes, encoding case type, emitted size, parameter, and literal flags.
- `Mask`: ARM64 logical-immediate mask descriptor used by `bits.c`.

Important enums and globals:
- Symbol classes: `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SFILE`, `SSTRING`, `SUNDEF`, `SIMPORT`, `SEXPORT`.
- Operand classes: register, stack pointer, shifts, constants, branches, auto/external offsets, pre/post-indexed operands, vector registers, and fallback classes.
- Mark flags: `FOLL`, `LABEL`, `LEAF`, `FLOAT`, `BRANCH`, `LOAD`, `SYNC`, `NOSCHED`.
- ARM64-specific constants: `STACKALIGN = 16`, `PCSZ = 8`, relocation bit splits `Roffset`/`Rindex`.
- Linker globals for output layout, buffers, symbol hash table, text/data instruction lists, dynamic import/export state, and literal-pool state.

Declared functions cover the whole linker pipeline:
- Object/archive loading: `objfile`, `ldobj`, `lookup`, `loadlib`.
- Control flow/layout: `patch`, `follow`, `span`, `noops`.
- Data and dynamic linking: `dodata`, `dynreloc`, `asmdyn`, `import`, `export`.
- Output: `asmb`, `asmout`, `asmsym`, buffered integer writers.
- Formatting and diagnostics: `listinit`, `%A/%D/%P/%S/%N/%R` formatters, `diag`.

Filesystem relevance: indirect. It defines the linker’s shared state and ABI contracts.
