# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regcomp.c

- Role: Local copy/variant of Plan 9 regexp compiler with adjusted allocation behavior.
- Key functions: `regcomp`, `regcomplit`, `regcompnl`; parser helpers build NFA instructions from regex syntax, character classes, alternation, concatenation, and repetition.
- Data structures: Operator and operand stacks, `Reinst` program, `Reclass` character classes.
- Integration: Consumed by `regen.c`, `dump.c`, and DFA conversion.
- Risks/notes: File header states it leaks extra classes when it runs out; fixed stack sizes (`NSTACK`) limit regex complexity.
