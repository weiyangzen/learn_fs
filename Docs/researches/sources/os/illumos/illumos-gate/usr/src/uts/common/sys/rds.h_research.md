# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rds.h

## Role

`rds.h` defines the user/kernel ABI for Reliable Datagram Sockets with RDMA support. It is imported from the OFED/Linux RDS interface and adapted for illumos/SVR4 type conventions.

## Socket Interface

The file defines:
- `AF_RDS`, `PF_RDS`, and `SOL_RDS`.
- socket options for canceling sent messages, memory-region get/free, receive errors, congestion monitoring, and destination-specific MR registration.
- control-message types for RDMA args, destination, memory mapping, RDMA status, and congestion updates.
- RDS info selectors for counters, connections, messages, sockets, TCP/IB/iWARP connections, and connection stats.

## Info Structures

The header defines packed info records for counters, connections, flows, messages, sockets, TCP sockets, and RDMA connections. It uses `#pragma pack(1)` and `__attribute__((packed))` outside lock-lint paths to preserve ABI layout.

Connection/message/socket records carry addresses, ports, sequence numbers, flags, buffer sizes, and transport names.

## Congestion and RDMA

Congestion monitoring uses a 64-bit port-group mask with `RDS_CONG_MONITOR_BIT()` and `RDS_CONG_MONITOR_MASK()`.

RDMA structures include:
- `rds_rdma_cookie_t`
- `rds_iovec`
- memory-region get/free args.
- destination-specific MR args.
- RDMA transfer args and completion notification.

Flags cover read/write permission, fence, invalidate, use-once, dontwait, and notify-me behavior.

## Research Notes

This is a protocol ABI header. The packed layouts, cross-platform integer typedefs, socket option numbers, and RDMA cookie/control-message formats are the main compatibility risks.
