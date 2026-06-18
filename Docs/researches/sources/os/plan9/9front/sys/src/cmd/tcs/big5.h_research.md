# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/big5.h

Declares constants and external storage for the Big5 mapping table.

Key points:
- Defines `BIG5MAX` as `13973`.
- Defines `BIG5FONT` as `157`.
- Declares `extern long tabbig5[BIG5MAX]`, described as runes indexed by Big5 ordinal.

Dependencies and interactions:
- Included by `big5.c` and charset conversion code using the Big5 table.

Research relevance:
- Small header that fixes the Big5 table size and public symbol.
