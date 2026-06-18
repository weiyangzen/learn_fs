# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/lookup.c

Symbol tables for `eqn`.

Key behavior:
- Defines keyword table mapping eqn syntax words to parser tokens.
- Defines reserved-word translations for mathematical symbols, Greek letters, relation operators, functions, and named output strings.
- Implements simple additive string hash, lookup, install/update, and table initialization.
- `init_tbl()` installs keywords/reserved words and initializes tuning definitions.

Filesystem relevance:
- In-memory parser table logic only.
