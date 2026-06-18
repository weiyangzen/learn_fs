# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_match.c

Implements a small SDP matching helper.

Key behavior:
- `sdp_match_uuid16` builds a Bluetooth-base UUID with the requested 16-bit value.
- Uses `sdp_get_uuid` on a local cursor copy.
- Advances the caller cursor only when the decoded UUID equals the requested UUID.

Dependencies:
- `sdp_get_uuid`, `BLUETOOTH_BASE_UUID`, and `uuid_equal`.
