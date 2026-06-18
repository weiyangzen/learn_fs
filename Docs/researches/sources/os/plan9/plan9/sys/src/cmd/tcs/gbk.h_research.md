# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.h

This header exposes the GBK table range and table symbol used by the `tcs` GBK converter.

Key contents:
- `GBKMIN` is `0x8140`.
- `GBKMAX` is `0xFE50`.
- `extern long tabgbk[];` declares the mapping array defined in `gbk.c`.

Important details:
- The range is treated as half-open by `conv_gbk.c`: valid table lookup requires `c >= GBKMIN && c < GBKMAX`.
- The required table length is therefore `GBKMAX - GBKMIN`, which matches the 32,016 initializer entries in `gbk.c`.
- The header does not describe byte validity itself; it only bounds the numeric packed-code table.

Filesystem relevance:
- Indirect: part of `tcs` character conversion support for file/stream text data.
