# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/rds/rds_transport.h

This small legacy RDS header defines the transport operations vector used by the socket layer to call the IB transport.

Core definitions:
- `rds_transport_ops_t` provides hooks to open/close IB, send a message, resume a port, and look up an interface by name.
- Global `rds_transport_ops` points to the active transport implementation.
- Extern tunables include user buffer size and RX pending packet high-water mark.

Risk-sensitive invariants:
- The socket layer depends on the transport vector being installed before send/open paths.
- Send hook carries source/destination IPs, ports, and zone ID, so transport must preserve zone isolation.
