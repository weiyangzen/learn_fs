# File Research: sources/virtualization/nvme-cli/libnvme/examples/mi-mctp-ae.c

This C example enables and processes NVMe-MI asynchronous event messages over MCTP.

Core behavior:
- Parses `<net> <eid> [AE numbers...]`.
- Opens an MCTP endpoint.
- Queries and prints previously enabled events.
- Builds `libnvme_mi_aem_config` with a handler and enabled event bitmap.
- Enables asynchronous event messages.
- Gets the AEM file descriptor and polls it alongside stdin.
- When AEM data is readable, calls `libnvme_mi_aem_process`.
- Handler drains events via `libnvme_mi_aem_get_next_event`, prints event fields, and returns ACK.
- Disables AEM and closes context on exit.

Important detail:
- Returns an explicit message for `EOPNOTSUPP`, noting that MCTP Peer-Bind is required for AEM.

Integration role:
- Demonstrates event-driven MI over MCTP with `poll()`.
