# File Research: sources/os/plan9/9front/sys/src/cmd/vl/l.h

This is the central private header for the MIPS linker `vl`.

Key contents:
- Defines linker IR structs: `Adr`, `Prog`, `Sym`, `Auto`, `Optab`, `Oprang`, `Count`, and opcode cross-reference storage.
- Defines symbol classes (`STEXT`, `SDATA`, `SBSS`, etc.), operand classes (`C_REG`, `C_SCON`, `C_LBRA`, etc.), scheduler flags, buffer limits, hash sizes, and scheduling window constants.
- Declares global linker state for headers, entry/data/text addresses, object buffers, symbol tables, current text/function state, line/symbol sizes, library lists, endian maps, and delay-slot statistics.
- Declares formatting, loading, patching, data layout, scheduling, span, assembly, symbol, and utility functions.

Integration and risks:
- Shared across all `vl` implementation files, so struct layout and enum values are ABI-like within the linker.
- `Adr` and `Prog` cache operand classes and optab indices; code that mutates operands must call `nocache`.
