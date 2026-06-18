# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_rmpp.h

## Scope

Defines private IBMF Reliable Multi-Packet Protocol (RMPP) context, header, states, packet types, flags, and status values.

## Structures And Constants

- `ibmf_rmpp_ctx_t` tracks send window first/last/next, expected receive segment, direction switch, new window last, payload length, state, retry count, packet data sizes, number of packets, data offset, cached header words, packet type, response time, flags, and status.
- RMPP states include undefined, sender active, sender switch, receiver active, receiver terminate, abort, and done.
- `IBMF_CTX_RMPP_FLAGS_DYN_PYLD` marks dynamic payload.
- Default response time values and method response bit constants are defined.
- `ibmf_rmpp_hdr_t` models the IB RMPP header with version, type, response time/flags bitfields, status, segment number, and payload-length/new-window-last field.
- Header bitfield order changes for `_BIT_FIELDS_HTOL` versus the default low-to-high layout.

## Protocol Values

- Types: none, data, ACK, STOP, ABORT.
- Flags: active, first packet, last packet.
- Statuses: normal, resources exhausted, total time too long, inconsistent last/payload length, inconsistent first/segment number, bad type, window too small, segment too big, illegal status, unsupported version, too many retries, unspecified error.
- `IBMF_RMPP_VERSION` is 1 and default window size is 5.

## Dependencies

- Embedded in `ibmf_msg_impl_t`.
- Used by IBMF RMPP send/receive helpers declared in `ibmf_impl.h`.

## Risks And Invariants

- Window and expected-segment fields drive retransmission and ACK behavior; off-by-one errors can stall or corrupt multi-packet transfers.
- Header status/type/flag values are wire protocol constants and must stay spec-compatible.
- Payload lengths and last-packet sizes must be consistent with segmented buffer offsets.
- Bitfield ordering must match target architecture conventions.
