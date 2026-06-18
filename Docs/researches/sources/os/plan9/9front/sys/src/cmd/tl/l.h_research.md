# File Research: sources/os/plan9/9front/sys/src/cmd/tl/l.h

`l.h` is the central shared header for the ARM linker.

Core types:
- `Adr`: instruction operand/address, with offset/string/IEEE payload and symbol/auto references.
- `Prog`: linked instruction record with operands, branch condition target, pc, line, opcode, condition, register, and cached class data.
- `Sym`: linker symbol with type, version, value, signature, Thumb/interworking flags, and use lists.
- `Autom`: automatic variable/history metadata.
- `Optab`: instruction selection table row.
- `Oprang`, `Count`, and `Use`: opcode ranges, counters, and symbol-use records.

Key constants:
- Symbol types: `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SUNDEF`, import/export types, etc.
- Operand classes: register, constants, branches, autos, externs, Thumb-specific classes, floating constants, etc.
- Mark flags: `FOLL`, `LABEL`, `LEAF`.
- Linker sizes and limits: `NHASH`, `NHUNK`, `MINSIZ`, `MAXIO`, `MAXHIST`.

Globals:
- Declares all shared linker state: text/data sizes, segment origins, debug flags, hash table, program lists, symbol output sizes, architecture flags, import/export state, opcode tables, etc.
- `EXTERN` toggles between declaration and definition; `obj.c` defines `EXTERN` before including this header.

Function prototypes:
- Covers all major phases: object load, data layout, patching, follow, noops, span, emit, formatting, import/export, Thumb helpers, and ARM encoding helpers.

Risk notes:
- Global mutable state is pervasive; phase ordering is critical.
- `CALLEEBX` is defined here and changes interworking code generation across multiple files.
