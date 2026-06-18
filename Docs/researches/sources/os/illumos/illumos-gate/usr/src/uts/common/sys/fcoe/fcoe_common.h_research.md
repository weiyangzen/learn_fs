# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fcoe/fcoe_common.h

## Role

`fcoe_common.h` defines the in-kernel common interface between the Fibre Channel over Ethernet core and its initiator/target clients. It covers FCoE status, FC frame layout as byte arrays, frame and port objects, client registration, byte-order helpers, FC header accessors, and FCP command/response payloads.

## FCoE Core Types

- Defines FCoE return values, 1G/10G port speeds, FC frame header size, FLOGI payload sizes, minimum MTU, and maximum FC frame size.
- Defines `fcoe_fc_frame_header_t` as byte arrays for all FC frame header fields to avoid endian-sensitive bitfield layout.
- `fcoe_frame_t` stores flags, network buffer, FC header and optional headers, FC frame and payload pointers, size/allocation fields, owning port, private client/core pointers, and timestamp.
- `fcoe_port_t` stores flags, private pointers, port/node WWNs, maximum FC frame size, MTU, link speed, Ethernet destination, and function vectors for transmit, frame allocation/release, netb allocation/free, client deregistration, control, and MAC address change.
- Port flags distinguish direct P2P, target mode, initiator mode, and MAC-in-use state.
- Notifications cover link up/down and address change. Port control commands cover online/offline.
- Defines FCoE version enum, current version `FCOE_VER_NOW`, and `fcoe_client_t` registration structure with client callbacks.

## Byte Order And Header Access

The header provides `FCOE_V2B_*` and `FCOE_B2V_*` macros for 1/2/3/4/8-byte big-endian value conversion, plus `FRM_*` getters and `FFM_*` setters for FC header fields. `FRM_IS_LAST_FRAME()` and `FRM_SENDER_IS_XCH_RESPONDER()` test F_CTL bits.

## FCP And Utility Definitions

- Declares `fcoe_register_client()`.
- Defines `EPORT_CLT_TYPE()`, default FCoE OUI/fabric-port MAC helpers, default/min FCP payload sizes, and `fcoe_fcp_cmnd_t`, `fcoe_fcp_rsp_t`, and `fcoe_fcp_xfer_rdy_t`.
- Defines `CURRENT_CLOCK`, seconds-to-ticks conversion, mod-hash key conversion helpers for exchange ids, taskq function pointer type, and `fcoe_trace()`.
