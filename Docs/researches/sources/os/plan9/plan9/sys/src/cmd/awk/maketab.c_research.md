# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/maketab.c

Build-time generator for `proctab.c`.

It reads token values from `y.tab.h`, emits a printable token-name table, and emits `proctab[]`, mapping yacc token numbers to interpreter functions used by `execute()` in `run.c`.

The static `proc[]` table is the authoritative mapping from syntax tokens such as `ADD`, `PRINT`, `CALL`, `MATCHFCN`, and `FOR` to runtime handlers such as `arith`, `printstat`, `call`, `matchop`, and `forstat`.
