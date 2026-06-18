# File Research: sources/os/plan9/plan9/sys/src/cmd/ql/l.h

PowerPC linker shared header for `ql`.

Defines the linker’s central IR and global state:
- `Adr`: assembler operand with value union, symbol, auto metadata, register/name/type/class fields.
- `Prog`: instruction node with `from`, `from3`, `to`, branch `cond`, list links, pc, mark flags, opcode, and register.
- `Sym`: linker symbol record with type/version/value/signature metadata.
- `Autom`: auto/history metadata attached to `TEXT`.
- `Optab`: instruction selection table entry.

Important enums cover:
- instruction mark bits such as `LABEL`, `LEAF`, `BRANCH`, `LOAD`, `SYNC`, `NOSCHED`;
- linker symbol classes such as `STEXT`, `SDATA`, `SBSS`, `SXREF`, `SIMPORT`, `SEXPORT`;
- operand classes such as `C_REG`, `C_SCON`, `C_LEXT`, `C_SBRA`, `C_ADDR`.

The file also declares all major global linker state: output/header layout, current text/prog pointers, symbol hash table, data/text sizes, object/library tracking, dynamic import/export counters, byte-order maps, and output buffers. It is the coupling point for the `ql` linker pipeline: object loading, branch patching, data layout, scheduling, instruction spanning, assembly output, profiling injection, and dynamic relocation.

Risk/notes:
- The design is intentionally global-state-heavy; ordering of passes matters.
- Operand class caching (`Adr.class`) is central to `oplook()` performance and correctness.
- `Roffset`/`Rindex` encode dynamic relocation limits and are checked later.
