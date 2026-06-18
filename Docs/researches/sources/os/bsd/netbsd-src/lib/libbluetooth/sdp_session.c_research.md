# File Research: sources/os/bsd/netbsd-src/lib/libbluetooth/sdp_session.c

Implements SDP session open/close and PDU send/receive primitives.

Key behavior:
- `_sdp_open` creates an L2CAP `SOCK_SEQPACKET` Bluetooth socket, enables `SO_LINGER`, binds to a local address or `BDADDR_ANY`, connects to remote `L2CAP_PSM_SDP`, reads incoming MTU, and allocates `ibuf`.
- `_sdp_open_local` connects to the local Unix-domain sdpd control socket, defaulting to `/var/run/sdp`, and uses `L2CAP_MTU_DEFAULT`.
- `_sdp_close` closes the socket and frees incoming/reassembly buffers.
- `_sdp_send_pdu` increments transaction ID, builds an SDP PDU header, validates parameter length fits `uint16_t`, and writes header plus iov payload with `writev`.
- `_sdp_recv_pdu` reads header and payload, validates PDU ID, transaction ID, and exact length, and maps SDP error responses to `errno`.
- `_sdp_errno` maps invalid record handle to `ENOATTR`; other SDP errors map to `EIO`.

Dependencies:
- Bluetooth L2CAP sockets, Unix-domain sockets, endian helpers, and `sdp-int.h`.

Notes:
- `ss->s` is zero-initialized by `calloc`; `_sdp_close` treats any descriptor not equal to `-1` as closable, so failure before socket creation can close descriptor 0.
