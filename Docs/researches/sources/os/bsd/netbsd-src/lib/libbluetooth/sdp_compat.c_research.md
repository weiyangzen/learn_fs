# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_compat.c

Implements the deprecated source-level SDP compatibility API enabled with `SDP_COMPAT`.

Key behavior:
- Wraps modern `sdp_session_t` in `struct sdp_compat` with a stored error and 256-byte scratch buffer.
- Provides old `sdp_open`, `sdp_open_local`, `sdp_close`, and `sdp_error`.
- `sdp_search` builds a service search pattern and attribute ID list, performs `sdp_service_search_attribute`, and maps response attributes into legacy `sdp_attr_t` slots.
- `sdp_register_service`, `sdp_change_service`, and `sdp_unregister_service` send old/control PDU requests and expect zero-valued SDP error responses.
- Provides `sdp_attr2desc` and `sdp_uuid2desc` lookup tables for common attribute and UUID descriptions.
- `sdp_print` delegates to `_sdp_data_print`.

Dependencies:
- Modern SDP internals from `sdp-int.h`.
- Compatibility definitions in `sdp.h`.

Notes and risks:
- `sdp_open` allocates `struct sdp_compat` with `malloc`; if called with null addresses, it sets `error` but leaves `ss` uninitialized, so a later `sdp_close` on that handle is unsafe.
- `sdp_search` ignores failed `sdp_put_*` calls while building the fixed 256-byte scratch request, relying on input sizes to fit.
