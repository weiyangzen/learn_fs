# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp-int.h

Private header for libbluetooth SDP internals.

Key behavior:
- Defines `struct sdp_session` with transaction ID, incoming MTU, incoming buffer, reassembly buffer, continuation-state buffer, and socket descriptor.
- Declares internal session functions `_sdp_open`, `_sdp_open_local`, `_sdp_close`, `_sdp_send_pdu`, `_sdp_recv_pdu`, and `_sdp_errno`.
- Declares internal SDP data printer `_sdp_data_print`.
- Re-declares `sdp_service_search_attribute` for internal use.

Dependencies:
- Public `sdp.h` types.

Notes:
- The continuation state buffer is 17 bytes: one length byte plus up to 16 continuation bytes.
