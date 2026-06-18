# File Research: sources/os/plan9/plan9/sys/src/cmd/eqn/tuning.c

Tuning constants for `eqn` layout.

Key behavior:
- Defines numeric parameters for script spacing, diacritics, fat text, large operators, integrals, matrices, fractions, delimiters, piles, sub/sup layout, and square roots.
- Defines default string expansions for accents, large operators, and integral symbol.
- Initializes tuning definitions into `deftbl` and tunable names into `ftunetbl`.
- `ftune()` allows definitions to adjust `Subbase` and `Supshift`.

Filesystem relevance:
- Typesetting configuration only.
