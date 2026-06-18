# File Research: sources/os/plan9/9front/sys/src/cmd/5l/l.h

This header defines the central data structures, enums, globals, macros, and function prototypes for the ARM linker `5l`.

Key elements:
- `Adr` represents operands, including offset/string/IEEE payloads and auto/symbol links.
- `Prog` represents linker IR instructions with operands, branch condition pointers, PC, line, opcode, condition flags, and register fields.
- `Sym` represents linker symbols with type, version, frame, value, signature, duplicate-ok state, and hash linkage.
- `Autom`, `Optab`, `Oprang`, `Opcross`, and `Count` support auto variables, opcode selection, and reporting.
- Symbol type enum includes `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SFILE`, `SCONST`, `SSTRING`, `SUNDEF`, `SIMPORT`, and `SEXPORT`.
- Operand class enum defines register, constants, branch ranges, stack/external/base-offset classes, auto/extern offset widths, and address classes.
- Global state covers output header/layout parameters, text/data lists, symbol hash, library queues, endian maps, opcode ranges, debug flags, DLM/import/export state, literal pools, and division helper symbols.
- Prototypes expose all major linker phases: object loading, patching, data layout, following, no-op/prologue processing, span, assembly, symbol output, operand classification, relocation, profiling insertion, and diagnostics.

Dependencies and integration:
- Includes Plan 9 `u.h`, `libc.h`, `bio.h`, ARM object format `../5c/5.out.h`, and shared compiler compatibility declarations.
- Shared by every `5l` source file in this group.

Research notes:
- `l.h` is the architectural contract between parser/object reader, linker passes, scheduler, span/operand classifier, and assembler output.
