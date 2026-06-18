# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/siinterp.h

Header for the image interpolation stream filter.

Key contents:
- Includes shared image scaling parameter definitions from `sisparam.h`.
- Exports `s_IIEncode_template`.

Notable dependencies:
- Requires `strimpl.h` when stream templates are referenced by the including compilation unit.

Research notes:
- This header exposes only the stream template; concrete state is private to `siinterp.c`.
