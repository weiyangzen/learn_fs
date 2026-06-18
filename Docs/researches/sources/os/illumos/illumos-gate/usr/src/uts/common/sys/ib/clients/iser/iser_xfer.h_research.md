# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/iser/iser_xfer.h

## Purpose

Defines iSER wire headers and transfer routines for connection private data, Hello/HelloReply exchange, iSCSI control PDUs, and RDMA data movement over an RC channel.

## Main Definitions

- `iser_private_data_t`: packed CM REQ private data containing IBT IP header private data plus SIE/ZBVA flags and reserved bytes, with endian-specific bitfield ordering.
- iSER opcode constants for control-type PDU, Hello, and HelloReply.
- `iser_ctrl_hdr_t`: expanded iSER control header used when ZBVA is not supported, including opcode, RStag/WStag valid flags, write stag/VA, and read stag/VA.
- `iser_hello_hdr_t`: Hello message with opcode, min/max version, and IRD.
- `iser_helloreply_hdr_t`: HelloReply with opcode, flag, current/max version, and ORD.
- `#pragma pack(1)` ensures these protocol headers are byte-packed.
- Transfer prototypes:
  - `iser_xfer_hello_msg()`
  - `iser_xfer_helloreply_msg()`
  - `iser_xfer_ctrlpdu()`
  - `iser_xfer_buf_to_ini()`
  - `iser_xfer_buf_from_ini()`

## Integration Notes

The structures are protocol ABI, not just internal state. They are used alongside connection-stage tracking in `iser.h` and channel/WR resources in `iser_ib.h` and `iser_resource.h`.

## Risks and Gotchas

- Requires one of `_BIT_FIELDS_LTOH` or `_BIT_FIELDS_HTOL`; incorrect endian macro selection changes wire bit positions.
- The header is packed to one-byte alignment; adding fields must preserve protocol layout.
- Control header use depends on ZBVA negotiation.
