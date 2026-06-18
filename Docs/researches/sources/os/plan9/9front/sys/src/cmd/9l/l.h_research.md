# File Research: sources/os/plan9/9front/sys/src/cmd/9l/l.h

This is the central header for the Power64 linker. It defines linker data structures, symbol classes, operand classes, global state, and function prototypes.

Key structures:
- `Adr`: assembler operand with offset/string/IEEE union, symbol, auto record, type, register, name, and class.
- `Prog`: instruction node with `from`, `from3`, `to`, branch/flow links, pc, mark flags, optab index, opcode, and register.
- `Sym`: linker symbol with type, version, value, signature, file, frame, and become metadata.
- `Autom`: auto/parameter/file-history metadata.
- `Optab`: operand pattern and encoder dispatch record.

Key enums and constants:
- Mark flags: `LABEL`, `LEAF`, `FLOAT`, `BRANCH`, `LOAD`, `FCMP`, `SYNC`, `FOLL`, `NOSCHED`.
- Symbol types: `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SLEAF`, `SCONST`, `SUNDEF`, `SIMPORT`, `SEXPORT`.
- Operand classes: `C_REG`, `C_FREG`, `C_ZCON`, `C_SCON`, `C_LCON`, `C_VCON`, `C_SBRA`, `C_LBRA`, `C_SAUTO`, `C_LEXT`, `C_ADDR`, etc.
- Relocation bit partition constants `Roffset` and `Rindex`.

Important interactions:
- Shared by all `9l` implementation files.
- Includes target opcode/address definitions from `../9c/9.out.h`.
- Declares global state such as `firstp`, `textp`, `datap`, `hash`, `HEADTYPE`, `INITTEXT`, `INITDAT`, `datsize`, `textsize`, `debug`, `oprange`, and dynamic import/export state.

Research notes:
- This header defines the linker’s internal ABI and must remain consistent with object records emitted by `9c`.
