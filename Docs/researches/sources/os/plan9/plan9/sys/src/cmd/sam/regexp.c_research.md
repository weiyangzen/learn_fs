# File Research: sources/os/plan9/plan9/sys/src/cmd/sam/regexp.c

Implements `sam` regular expression compilation and forward/backward execution.

Key components:
- `Inst` is the compiled NFA instruction format, with literal, operator, branch, class, and subexpression marker variants.
- Parser stacks (`andstack`, `atorstack`, `subidstack`) implement precedence parsing for concatenation, alternation, repetition, grouping, and character classes.
- `compile` builds both forward `startinst` and backward `bstartinst` programs, then optimizes NOP chains.
- `execute` scans forward from a start position, with wraparound behavior for unbounded search.
- `bexecute` scans backward using a separately compiled reversed machine.
- `sel` stores selected subexpression ranges.

Supported regex features:
- Literals, escapes including `\n`, `.`, `^`, `$`, `[]`, `[^]`, `*`, `+`, `?`, `|`, and parentheses.
- Character-class ranges are encoded with `Runemax` sentinels.
- Subexpressions beyond `NSUBEXP` are silently ignored.

Risk/maintenance notes:
- Fixed limits include `NPROG`, `NLIST`, and parser `NSTACK`.
- Matching is global-state driven and reports errors by clearing `lastregexp` and calling `error`.
