# File Research: sources/os/plan9/plan9/sys/src/cmd/astro/cosadd.c

Helper for compact trigonometric perturbation series evaluation.

Key points:
- `icosadd` initializes global coefficient and argument-multiplier streams.
- `cosadd` and `sinadd` consume coefficient pairs and signed char multipliers until a zero coefficient sentinel.
- Each term evaluates a base angle plus a linear combination of passed coefficients.

Dependencies:
- Used by Sun, Mercury, Venus, and nutation coefficient tables.

Notable behavior:
- Advances global `cafp` and `cacp` as series terms are consumed.
