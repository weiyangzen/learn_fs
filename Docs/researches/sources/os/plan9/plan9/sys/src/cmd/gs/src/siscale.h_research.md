# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siscale.h

Header for the smoothed image scaling stream filter.

Key contents:
- Includes shared image scaling parameter definitions from `sisparam.h`.
- Exports `s_IScale_template`.

Notable dependencies:
- Requires stream template context from `strimpl.h` in users.

Research notes:
- Concrete scaler state and implementation are private to `siscale.c`.
