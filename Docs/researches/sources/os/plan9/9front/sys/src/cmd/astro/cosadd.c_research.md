# File Research: sources/os/plan9/9front/sys/src/cmd/astro/cosadd.c

Shared periodic-series evaluator for the astronomy modules.

Important behavior:
- `icosadd` selects the active coefficient and integer-multiplier tables.
- `cosadd` and `sinadd` iterate coefficient pairs until a zero sentinel and add cosine/sine terms.
- Variadic arguments are the base angular arguments multiplied by signed byte coefficients from `cacp`.

This supports compact encoded perturbation tables in the planet, Sun, and nutation modules.
