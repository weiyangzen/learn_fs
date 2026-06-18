# File Research: sources/os/plan9/plan9/sys/src/cmd/units.y

Read fully: 786 lines, 10979 bytes. SHA-256 prefix: `1827c4bd74cb6c31`.

This is the yacc grammar and evaluator for Plan 9 `units`. It reads a units database, builds dimensional expressions, then interactively converts “you have” and “you want” quantities.

Core structures:
- `Node`: numeric value plus up to `Ndim` signed dimension exponents.
- `Var`: hashed unit name to `Node`.
- `Prefix`: metric prefix table, including Greek micro.

Grammar supports definitions (`: name expr`), fundamental dimensions (`: name #`), queries (`? expr`), arithmetic, implicit multiplication, division, powers, superscript 1/2/3, and parenthesized expressions.

Important routines:
- `yylex()` tokenizes runes, names, numeric values, multiplication/division symbols, and superscripts.
- `lookup()` hashes names and resolves metric prefixes/plural `s` suffixes.
- `add()`, `sub()`, `mul()`, `div()`, and `xpn()` compute values and dimensions.
- `specialcase()` handles Celsius/Fahrenheit offset conversions.
- `Ufmt()` prints values with numerator and denominator dimensions.
- `fmul()` and `fdiv()` guard overflow/underflow with logarithms.

Risk notes: the dimensional limit is fixed at 15, names at 40 runes, and query state alternates by line number.
