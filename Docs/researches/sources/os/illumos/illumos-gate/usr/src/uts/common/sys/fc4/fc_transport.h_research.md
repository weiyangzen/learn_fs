# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc_transport.h

## Role

`fc_transport.h` defines a generic Fibre Channel adapter transport interface for child FC protocol drivers. It wraps FC packets, completion callbacks, transport status codes, unsolicited command handling, state change registration, and function vectors exposed by FC adapters.

## Packet And Status Model

- Defines `fc_devdata_t`, `fc_ioclass_t`, `fc_iotype_t`, `fc_sleep_t`, and `fc_statec_t`.
- `fc_packet_t` carries adapter cookie, completion/private data, flags, timeout, I/O class/device data, command/response/data segments, completion status/statistics, command/response frame headers, and packet-chain links.
- Packet flags include `FCFLAG_NOINTR` and `FCFLAG_COMPLETE`.
- Transport return values include success, failure, timeout, queue full, and unavailable.
- `fc_pkt_status` values include OK, P_RJT/F_RJT, P_BSY/F_BSY, offline, timeout, overrun, queue/exchange/resource errors, and pseudo-status values for login timeout, CQ full, transport failure, and reset failure.

## Transport Vectors

`fc_transport_t` exposes adapter cookie, DMA limits/attributes, interrupt cookie, lock/cv, and operations:

- Submit/reset packets.
- Allocate/free packets.
- Register/unregister state change callbacks.
- Poll the interface for error recovery when interrupts are disabled.
- Register/unregister unsolicited command callbacks.
- Fetch unsolicited command payload into a caller-provided packet.
