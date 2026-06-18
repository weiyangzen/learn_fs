# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sbtx.h

Declares ByteTranslate encode/decode filter state. The state is simply stream common fields plus a 256-byte translation table, with encode and decode using the same structure type aliases.

It exposes `s_BTE_template` and `s_BTD_template`; implementation lives in `sfilter1.c`.

This is byte mapping stream support, not filesystem logic.
