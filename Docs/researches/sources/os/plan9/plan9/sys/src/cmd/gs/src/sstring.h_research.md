# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/sstring.h

Header for ASCIIHex and PostScript string stream filters.

Key contents:
- Defines `stream_AXE_state` with `EndOfData` and line-count state.
- Defines `stream_AXD_state` with odd hex digit state.
- Defines `stream_PSSD_state` with `from_string` and parenthesis depth.
- Declares init macros, concrete init for `PSStringDecode`, and stream templates for ASCIIHexEncode/Decode and PSStringEncode/Decode.

Notable dependencies:
- Requires stream common definitions in users.

Research notes:
- `s_PSSD_partially_init_inline` intentionally does not initialize `from_string`, allowing scanner-specific setup.
