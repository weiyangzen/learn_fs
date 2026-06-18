# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi-mctp.c

MCTP transport implementation for NVMe-MI endpoints.

Key behavior:
- Uses Linux `AF_MCTP` datagram sockets for NVMe-MI messages.
- Provides compatibility definitions for older MCTP tag allocation ioctls.
- Keeps transport state in `struct libnvme_mi_transport_mctp`: network ID, endpoint ID, command socket, AEM socket, and reusable response buffers.
- Abstracts socket operations through `struct __mi_mctp_socket_ops`, allowing tests to override socket/send/recv/poll/ioctl behavior.
- Allocates and drops MCTP tags where supported; falls back to owner-tag behavior if explicit allocation is unavailable.
- Sends MI requests as iovec fragments:
  - header excluding MCTP type byte
  - optional payload
  - MIC
- Receives responses into a linear buffer, restores the MCTP type byte, splits header/data/MIC back into libnvme response structures, and preserves MIC for upper-layer validation.
- Handles “More Processing Required” responses in the transport layer so the MCTP tag remains allocated while waiting for the final response.
- Provides AEM support:
  - opens a nonblocking AEM socket
  - returns pollable fd
  - purges pending AEM datagrams
  - reads async event messages
- Provides endpoint descriptions like `mctp: net <id> eid <id>`.
- With `CONFIG_DBUS`, scans `mctpd` over D-Bus for endpoints supporting NVMe-MI message type and adds them to a new global context.
- Without `CONFIG_DBUS`, `libnvme_mi_scan_mctp()` returns `NULL`.

Research notes:
- Transport `mic_enabled = true`, so upper layers calculate and verify CRC/MIC for MCTP.
- Default opened endpoint timeout is set to 5000 ms, based on conservative MCTP-over-I2C timing.
- Response buffer allocation grows dynamically when requested response size exceeds the cached buffer.
- The D-Bus scan path de-duplicates by `(network, eid)`.
