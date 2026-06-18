# File Research: sources/os/plan9/9front/sys/src/cmd/sat.c

Purpose: Command-line SAT front end that parses symbolic clauses and cardinality ranges, feeds them into Plan 9's `libsat`, and prints satisfying assignments.

Key structures:
- `Trie`: hash-trie node keyed by 64-bit FNV-like variable-name hash.
- `Var`: trie leaf with variable name, SAT variable number, and insertion-order list link.

Key routines:
- `hash`, `ctz`, `trieget`, `varget`: intern variable names and assign stable positive SAT IDs.
- `lex`: tokenizes variables, comments, brackets, punctuation, and newlines.
- `clause`: parses a clause line. Plain variable lists become OR clauses through `satadd1`; `[min,max]` prefixes become cardinality constraints through `satrange1`.
- `main`: handles `-1` for one positive-name model, `-m` for all models through `satmore`, or default output of each variable's signed value.

Integration: Depends on `<sat.h>` APIs `satnew`, `satadd1`, `satrange1`, `satsolve`, `satmore`, and `satval`.

Risks and limits:
- `lexbuf` truncates variable tokens beyond 511 bytes.
- Hash collisions are resolved by chaining off the trie leaf.
- Cardinality syntax is strict; malformed ranges call `sysfatal`.
