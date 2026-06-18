# File Research: sources/os/plan9/9front/sys/src/cmd/troff2html/chars.h

This header provides character translation tables for `troff2html.c`.

`htmlchars[]` maps UTF-8 characters to HTML entity strings or ASCII fallbacks. It is sorted by Unicode value after runtime initialization because `troff2html.c` fills each entry’s rune value and then binary-searches it.

`troffchars[]` maps troff named characters such as `A*`, `ff`, `em`, `hy`, `mu`, arrows, math symbols, brackets, and rule characters to HTML entities or rough text substitutes. Coverage is pragmatic rather than complete; unsupported troff names return `??` in the caller.
