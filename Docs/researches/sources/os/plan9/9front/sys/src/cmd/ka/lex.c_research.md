# File Research: sources/os/plan9/9front/sys/src/cmd/ka/lex.c

SPARC assembler front-end for the `ka` tool. It initializes target identity (`thechar='k'`, `thestring="sparc"`), parses assembler options, supports parallel assembly of multiple files on non-Windows hosts, and runs the assembler in two passes. The large `itab` table binds register names, pseudo-registers, opcodes, branches, traps, floating-point operations, and scheduling controls into the lexer symbol table.

Object output is encoded through `zname`, `zaddr`, and `outcode`, using compact symbol cache slots and little byte writes for offsets/floating constants. `outhist` serializes source history path elements as `ANAME`/`AHISTORY` records, with Windows path handling. The file ends by including shared C compiler lexer/macro/compat bodies from `../cc`, so this is architecture-specific setup around common Plan 9 compiler infrastructure.
