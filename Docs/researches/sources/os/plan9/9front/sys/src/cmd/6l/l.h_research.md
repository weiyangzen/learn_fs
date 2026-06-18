# File Research: sources/os/plan9/9front/sys/src/cmd/6l/l.h

- Role: Central header for the amd64 linker `6l`.
- Defines linker-side `Adr`, `Prog`, `Auto`, `Sym`, `Optab`, and `Movtab` structures.
- Enumerates symbol types (`STEXT`, `SDATA`, `SBSS`, `SXREF`, `SUNDEF`, import/export types), operand classes (`Y*`), encoding templates (`Z*`), opcode prefixes (`P*`), and REX flag bits.
- Declares global linker state: output buffers, header constants, data/text sizes, symbol hash table, instruction tables, register maps, current program/text pointers, dynamic relocation state, library lists, import/export counters, and formatting strings.
- Provides prototypes for all linker phases: object loading, library loading, branch patching, code following, data layout, stack fixup, spanning/encoding, output assembly, symbol/line table emission, dynamic relocation, import/export handling, and diagnostics.
- Couples 6l to `../6c/6.out.h`, meaning compiler, assembler, and linker share amd64 opcode/address enum definitions.
