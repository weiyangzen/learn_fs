# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_service.c

Implements SDP service search and attribute transactions.

Key behavior:
- Uses a default attribute ID list requesting `0x0000-0xffff` when callers pass `ail == NULL`.
- `sdp_response_max` reads `SDP_RESPONSE_MAX` once with an atomic guard, defaulting to `UINT16_MAX` and accepting values from `UINT8_MAX` to `UINT32_MAX`.
- `sdp_service_search` sends repeated `SERVICE_SEARCH_REQUEST` PDUs, follows continuation state, validates counts, and fills service record handles.
- `sdp_service_attribute` sends repeated `SERVICE_ATTRIBUTE_REQUEST` PDUs, reassembles attribute fragments into `ss->rbuf`, validates the final SDP sequence, and returns the inner sequence cursor.
- `sdp_service_search_attribute` does the same for `SERVICE_SEARCH_ATTRIBUTE_REQUEST`.
- Continuation state is limited to the SDP maximum 16 bytes.

Dependencies:
- `sdp-int.h` session helpers.
- SDP data encoders/validators/getters.
- `<sys/atomic.h>` for one-time environment parsing.

Notes and risks:
- Reassembly uses `realloc` on the session buffer; the returned `sdp_data_t` points into session-owned storage.
- Malformed counts, invalid continuation state, invalid SDP encoding, or oversized response all fail with `EIO`.
