# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/srlx.h

Defines RunLength encode/decode stream state.

Key points:
- Shared state includes `EndOfData`, controlling whether byte 128 is treated/emitted as EOD.
- `stream_RLE_state` adds record size, record bytes left, and pending literal-copy count.
- Encode defaults enable EOD and set record size to unlimited by default.
- `stream_RLD_state` tracks pending output byte count and whether pending data is literal copy or repeated byte.
- Decode defaults enable EOD and set `min_left` accordingly.
- Declares encode and decode templates.

Research relevance:
- Shared header for Ghostscript RunLength filters.
