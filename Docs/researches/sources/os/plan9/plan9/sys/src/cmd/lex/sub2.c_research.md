# File Research: sources/os/plan9/plan9/sys/src/cmd/lex/sub2.c

Read fully: 851 lines, 17044 bytes. SHA-256 prefix: `87e0fc10f8d6afdc`.

This file is the DFA construction and table-packing backend for `lex`. It computes follow sets, initial states, transitions, fallback states, action tables, character-class compression, and final `yycrank`, `yysvec`, `yymatch`, and `yyextra` output.

Key routines:
- `cfoll()`, `follow()`, and `first()` compute regex follow/first-position sets.
- `add()` and optional `padd()` store position sets.
- `cgoto()` creates DFA states for each start condition and line-begin variant, computes transitions, and emits `yyvstop`.
- `nextstate()` calculates destination position sets for a state/character.
- `notin()` interns/reuses existing states.
- `packtrans()` compresses transitions, optionally using character-class representatives and fallback states.
- `acompute()` generates ordered action lists for final states and right-context handling.
- `mkmatch()` creates fallback character representatives.
- `layout()` packs transition tables into the final generated C arrays.

Integration: consumes parse-tree arrays from parser/sub1 and writes generated code to `fout`.

Risk notes: this is table-size sensitive. `nextstate()` is called for every state/character pair and is noted as the dominant CPU cost.
