# File Research: sources/os/plan9/9front/sys/src/cmd/astro/moont.c

Lunar perturbation coefficient table.

Important contents:
- `moontab` is a sequence of coefficient plus four integer argument multipliers.
- Zero rows separate longitude, latitude, node, and parallax term groups consumed by `moon.c`.
- Values are used by `sinx`/`cosx` with lunar argument globals.

This file is data-only and has no executable logic beyond table initialization.
