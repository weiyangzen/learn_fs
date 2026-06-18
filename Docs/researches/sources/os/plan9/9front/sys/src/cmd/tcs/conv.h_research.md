# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/conv.h

Declares conversion-function entry points shared by the non-table encoders/decoders.

Key points:
- Declares input functions for JIS variants, Big5, GB2312, GBK, Korean EUC/KSC, HTML entities, and Tune.
- Declares output functions for the same function-backed encodings.
- Defines `emit(x)` as `*(*r)++ = (x)`, the common decoder helper for appending a Rune.
- Defines `NRUNE` as `65536`.
- Declares global `long tab[]`, a shared reverse-lookup table indexed by Rune values for output conversion.

Dependencies and interactions:
- Included by conversion implementations such as `conv_big5.c`, `conv_gb.c`, `conv_gbk.c`, `conv_jis.c`, and `conv_ksc.c`.
- Function pointers are registered from `tcs.c`.

Research relevance:
- Central ABI-like header for `tcs` state-machine conversions.
