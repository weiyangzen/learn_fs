# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fc4/fc.h

## Role

`fc.h` defines Fibre Channel Physical and Signaling Interface constants and payload structures for common FC frame handling. It is a protocol-level header used by FC drivers and FC-4 consumers.

## Frame Header And Control Bits

- Defines `FC_PH_VERSION` and `MAX_FRAME_SIZE`.
- Defines `fc_frame_header_t` with FC-2 frame fields: routing/control, destination/source ids, type, frame control, sequence ids/count, exchange ids, and relative offset/parameter.
- Provides header predicate macros for originator context, unsolicited frame, first/last sequence, last frame, and sequence initiative.
- Defines `r_ctl` routing and info masks plus device-data, extended service, FC-4 service, video, basic service, and link-control routing values.
- Defines device data categories, BLS codes, ELS request/response codes, ELS command opcodes, link-control codes, type values, and `F_CTL_*` bits.

## Addresses And Error Codes

Defines well-known FC addresses for multicast, management/time/name/fabric services, fabric F-port, and broadcast. It also defines busy/reject reason codes for fabric/N-port busy, frame reject, BA_RJT, and LS_RJT.

## Payload Structures

Defines reject parameters, transfer-ready payload, link-error-status reply, login payload, generic ELS payload, and `fc_dataseg_t` data segments with 32-bit base/count.
