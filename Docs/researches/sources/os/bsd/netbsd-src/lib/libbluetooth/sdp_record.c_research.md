# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_record.c

Implements NetBSD-local sdpd record management transactions.

Key behavior:
- `sdp_record_insert` sends `SDP_PDU_RECORD_INSERT_REQUEST` with a Bluetooth device address and service record sequence, then extracts the returned handle.
- `sdp_record_update` sends `SDP_PDU_RECORD_UPDATE_REQUEST` with handle and record sequence.
- `sdp_record_remove` sends `SDP_PDU_RECORD_REMOVE_REQUEST` with handle.
- All expect `SDP_PDU_ERROR_RESPONSE` with error code zero as success.
- Nonzero SDP error codes are translated with `_sdp_errno`.

Dependencies:
- Private session send/receive helpers from `sdp-int.h`.
- SDP sequence encoder and endian helpers.

Notes:
- These PDU IDs are documented in the file as sdpd control-socket extensions, not Bluetooth specification PDUs.
