# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibmf/ibmf_msg.h

## Scope

Defines the public IBMF message, local/global address, and message buffer structures used by `ibmf_msg_transport()` and receive callbacks.

## Structures

- `IBMF_MAD_SIZE` is 256 bytes.
- `ibmf_addr_info_t` stores local LID, remote LID, remote QPN, P_Key, Q_Key, and 4-bit service level.
- `ibmf_global_addr_info_t` stores sender/receiver GIDs, flow label, traffic class, and hop limit.
- `ibmf_msg_bufs_t` splits a message into MAD header, class header, and class data buffers with lengths.
- `ibmf_msg_t` contains local/global address info, completion status, message flags, message size limit, send buffers, and receive buffers.

## Buffer Contracts

- The MAD header is normally 24 bytes and may be NULL only for raw UD traffic over an appropriately allocated non-special QP.
- The class header may be separate or combined with class data by leaving `im_bufs_cl_hdr` NULL.
- For raw UD sends, the entire packet is supplied as class data and MAD/class header pointers should be NULL.
- MAD header, class header, and class data buffers contain IB wire-format big-endian data.
- Other fields in `ibmf_msg_t` are host-format.

## Dependencies

- Uses `ib_mad_hdr_t` from `ib_mad.h` and IB addressing scalar types.
- Included by public IBMF API and private implementation.

## Risks And Invariants

- Send buffers are client-owned; receive buffers are IBMF-owned.
- `im_msg_flags` must include `IBMF_MSG_FLAGS_GLOBAL_ADDRESS` when global address data is valid.
- Local/remote LID semantics reverse depending on send path versus receive callback context.
- Class-header offset/length must match the specific management class, especially for RMPP-capable classes where the RMPP header is not part of the class header buffer.
