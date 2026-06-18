# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_get.c

Implements typed SDP data extraction helpers.

Key behavior:
- All helpers advance the source cursor only after successful extraction.
- `sdp_get_data` slices the next encoded element.
- `sdp_get_attr` reads a `uint16` attribute ID followed by a value element.
- `sdp_get_uuid` expands 16-bit and 32-bit Bluetooth UUID aliases into `BLUETOOTH_BASE_UUID`, or decodes full 128-bit UUIDs.
- `sdp_get_bool`, `sdp_get_uint`, and `sdp_get_int` decode fixed-width scalar elements with bounds checks.
- 128-bit integer decoding succeeds only when the value fits in `uintmax_t` or `intmax_t`.
- `sdp_get_seq`, `sdp_get_alt`, `sdp_get_str`, and `sdp_get_url` use a shared variable-length extractor.

Dependencies:
- `sdp_data_size`, `sdp_data_type`, endian decode helpers, and UUID helpers.

Notes:
- Returned string and URL pointers reference the original buffer; they are not NUL-terminated copies.
