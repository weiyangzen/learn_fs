# File Research: sources/os/plan9/9front/sys/src/cmd/lex/sub2.c

`sub2.c` implements follow-position computation, DFA construction, transition packing, action table construction, character-class matching, and final scanner table layout.

Key functions:
- `cfoll()`, `follow()`, `first()`, `add()`, and `padd()` compute and pack position/follow sets from the regex parse tree.
- `cgoto()` creates initial states for start conditions, enumerates transitions for each DFA state, discovers new states with `notin()`, and emits `yyvstop`.
- `nextstate()` computes the target position set for a state/character pair.
- `packtrans()` compresses transitions using character-class representative matching and fallback states.
- `member()` tests packed character-class membership.
- `acompute()` builds per-state action lists including trailing-context fallback actions.
- `mkmatch()` builds `yymatch` representative-character mapping.
- `layout()` packs transition tables into `yycrank`, emits `yysvec`, `yymatch`, and `yyextra`.

This is the automata/code-generation core of Plan 9 `lex`.
