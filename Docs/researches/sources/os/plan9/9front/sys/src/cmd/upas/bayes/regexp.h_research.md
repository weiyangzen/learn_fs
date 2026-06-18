# File Research: sources/os/plan9/9front/sys/src/cmd/upas/bayes/regexp.h

This public regexp header defines the data model exposed by the local bayes regexp compiler/runtime.

Key contents:
- Defines `Resub` as start/end pointers for byte strings or rune strings.
- Defines `Reclass` as up to 64 rune span endpoints.
- Defines `Reinst`, whose first union stores class/rune/subexpression/right-branch data and whose second union stores left branch or next instruction.
- Defines `Reprog` with a `startinst`, embedded class storage, and flexible first instruction array.
- Declares `regcomp`, `regcomplit`, `regcompnl`, `regerror`, `regexec`, `regsub`, rune variants, and substitution helpers.

Integration and risks:
- `Reinst` union layout is relied on by compiler relocation code and execution code.
- `Reprog.firstinst[5]` is used as a flexible trailing array in practice; callers must allocate larger blocks, as `regcomp.c` does.
