# File Research: sources/os/plan9/9front/sys/src/cmd/astro/sunt.c

Sun perturbation coefficient tables.

Important contents:
- `sunfp` stores coefficient/phase pairs grouped by zero sentinels.
- `suncp` stores corresponding signed argument multipliers.
- Used by `sun.c` through `cosadd` and `sinadd`.

This is data-only support for solar position corrections.
