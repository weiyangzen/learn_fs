# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sstring.h

Defines string and hex string filter states/templates.

Key points:
- `stream_AXE_state` stores `EndOfData` and line-count state for ASCIIHexEncode.
- `stream_AXD_state` stores an odd hex digit for ASCIIHexDecode.
- `stream_PSSD_state` stores `from_string` and parenthesis depth for PSStringDecode.
- Provides inline initializers for ASCIIHex encode/decode and partial PSStringDecode initialization.
- Declares `s_AXE_template`, `s_AXD_template`, `s_PSSE_template`, `s_PSSD_template`, and `s_PSSD_init`.

Research relevance:
- Header contract for Ghostscript string and hex stream filters.
