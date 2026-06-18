# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_put.c

Implements SDP data encoding helpers.

Key behavior:
- `sdp_put_data` copies an existing encoded element/list into the destination cursor.
- `sdp_put_attr` writes a `uint16` attribute ID and a validated encoded value.
- `sdp_put_uuid` chooses 16-bit, 32-bit, or 128-bit encoding based on the Bluetooth base UUID and `time_low`.
- Scalar put functions encode bool, signed integers, and unsigned integers in the smallest fitting SDP width.
- `_sdp_put_ext` chooses 8-, 16-, or 32-bit variable-length headers for sequences, alternatives, strings, and URLs.
- `sdp_put_seq`, `sdp_put_alt`, `sdp_put_str`, and `sdp_put_url` use `_sdp_put_ext`.

Dependencies:
- Public `sdp.h`, endian encode helpers, UUID encode/equality helpers, and `strlen`.

Notes and risks:
- When `_sdp_put_ext` is called with `len == -1`, it estimates payload size from the remaining destination space and adjusts header width; callers must understand that this does not later patch based on actual content length.
