# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_data.c

Implements SDP element sizing, validation, and human-readable printing.

Key behavior:
- `sdp_data_type` returns the first element tag or `-1` if no tag is available.
- `sdp_data_size` computes the total encoded size of the first element, including variable-length headers.
- `sdp_data_valid` recursively validates an SDP element list, checking tag types, fixed widths, variable lengths, and nested sequence/alternative contents.
- `_sdp_data_print` walks an element list and prints nil, bool, signed/unsigned integers, UUIDs, strings, URLs, sequences, and alternatives with indentation.
- String/URL printing uses `vis` escaping and truncates long display output.
- `sdp_data_print` prints `SDP data error` when parsing fails.

Dependencies:
- Public `sdp.h`, private `sdp-int.h`, endian decoding helpers, and `vis`.

Notes:
- Validation is recursive and entirely bounds-driven; it does not enforce semantic constraints beyond legal encoding shape.
