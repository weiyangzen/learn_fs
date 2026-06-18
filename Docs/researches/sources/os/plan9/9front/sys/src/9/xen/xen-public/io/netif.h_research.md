# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/netif.h

Imported Xen public network frontend/backend protocol ABI.

Purpose:
- Defines Xen split network-device rings, packet descriptors, checksum/offload flags, multicast/GSO extra info, and response codes.

Key content:
- Defines minimum slot support `XEN_NETIF_NR_SLOTS_MIN`.
- Documents notification behavior and split event-channel feature.
- Documents TX wire format for chained request descriptors and optional extra descriptors.
- Defines TX flags for checksum blank, data validated, more data, and extra info.
- Defines `struct netif_tx_request`, `struct netif_extra_info`, `struct netif_tx_response`, `struct netif_rx_request`, and `struct netif_rx_response`.
- Defines RX flags, GSO/multicast extra-info types, and response codes.
- Generates TX and RX ring types with `DEFINE_RING_TYPES`.

Integration:
- Directly used by 9front’s `etherxen.c` Xen network driver.
- Uses grant references for packet buffers and event channels for notifications.
- Shares `ring.h` ordering and notification rules with the block driver.

Risks/notes:
- Multi-slot packet and extra-info chains require careful validation to avoid malformed frontend/backend traffic.
- Offload flags must match packet contents; incorrect checksum flags can corrupt networking.
