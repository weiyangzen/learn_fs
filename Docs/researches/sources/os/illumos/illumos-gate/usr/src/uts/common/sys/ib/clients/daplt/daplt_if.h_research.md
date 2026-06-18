# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt_if.h

## Purpose

Defines the user/kernel ioctl ABI for the `daplt` uDAPL kernel agent, including command numbers, driver naming, packed data structures, connection private data format, HCA-specific opaque return buffers, and ioctl payloads for IA, EP, EVD, MR, MW, PD, SP, CNO, and SRQ operations.

## Main Definitions

- `DAPL_IF_VERSION` and ioctl command namespaces by object type.
- Commands for IA creation/query, EP create/free/connect/modify/disconnect/reinit, EVD create/free/poll/wakeup/CQ resize/CNO modify, MR register/deregister/sync, MW alloc/free, CNO alloc/free/wait, PD alloc/free, service register/deregister, CR accept/reject/handoff, and SRQ create/free/resize.
- Driver name, minor name, default path, and event poll limits.
- `DAT_EVD_FLAGS` fallback definitions when DAT headers are not present.
- `#pragma pack(4)` around ioctl structures when 64-bit kernel long-long alignment differs from 32-bit ABI alignment.
- `dapl_ia_addr_t`, `DAPL_HELLO_MSG`, and `DAPL_PRIVATE`: DAPL private data/hello message format carrying IPv4, IPv6, or SA-address data.
- Opaque HCA-specific output arrays for CQ, QP, and SRQ creation/resize.
- EP ioctl structs for create, modify, connect, disconnect, reinit, and free.
- EVD event-family definitions and event return structures for async and CM events, plus 64-bit and 32-bit event-poll payloads.
- MR registration variants: direct, shared, LMR-based, deregister, and RDMA sync vectors.
- IA creation/query/enum structures and a stable copy of selected HCA attributes.
- PD, MW, SP, CR, CNO, and SRQ ioctl payload definitions.

## Integration Notes

This header is ABI-sensitive. It deliberately avoids direct kernel pointer fields in ioctl payloads except where a 32-bit shadow form is provided, and it uses fixed-width hash keys/cookies as user-visible handles.

## Risks and Gotchas

- Structure packing and padding are part of the ABI; changing field order or alignment breaks 32-bit userland on 64-bit kernels.
- `dapl_cq_data_out_t` and `dapl_qp_data_out_t` typedef names appear swapped in their array-size macros, but both sizes are currently 24 so behavior is unaffected.
- Private data length limits must stay consistent with IBT private-data limits.
- Event polling allocates kernel memory, hence `DAPL_EVD_MAX_EVENTS` bounds user requests.
