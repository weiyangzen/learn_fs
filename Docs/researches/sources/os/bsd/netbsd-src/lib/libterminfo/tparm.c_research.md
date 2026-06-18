# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/tparm.c

Parameterized terminfo string evaluator.

Key responsibilities:
- Implements a stack-based interpreter for terminfo `%` expressions.
- Supports:
  - numeric and string parameters,
  - `%p[1-9]`,
  - `%P`/`%g` dynamic and static variables,
  - `%i`,
  - character and integer constants,
  - arithmetic,
  - bit operations,
  - logical operations,
  - conditionals `%? %t %e %;`,
  - formatted numeric/string output.
- Analyzes parameter usage to decide which arguments are strings.
- Maintains per-terminal output buffer and static variables.
- Provides non-thread-safe fallback state through a dummy terminal for classic APIs.

Public functions:
- `ti_tiparm`
- `tiparm`
- `tparm`
- optional `ti_tlparm` / `tlparm` block is present but gated.

Role in subsystem:
- Expands cursor-addressing and other parameterized terminal capability strings before output.
