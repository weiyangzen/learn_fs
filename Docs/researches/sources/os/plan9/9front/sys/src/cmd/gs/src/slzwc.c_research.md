# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/slzwc.c

Contains code common to LZW encode and decode streams.

Key points:
- Defines the public GC structure descriptor for `stream_LZW_state`.
- `s_LZW_set_defaults` delegates to the inline defaults from `slzwx.h`.
- `s_LZW_release` frees the LZW table pointer stored in the decode/encode union.

Dependencies and interactions:
- Shared by `slzwd.c` and `slzwe.c`.

Research relevance:
- Common state lifetime support for LZW filters.
