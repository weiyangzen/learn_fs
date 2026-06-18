# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/rdma/ib_user_verbs.h

## Purpose

Defines the OFED user verbs ABI for illumos, including command IDs and request/response structures for contexts, device/port/GID/P_Key queries, PD/MR/CQ/QP/AH/SRQ lifecycle, posting send/receive work requests, polling completions, and multicast attach/detach.

## Main Definitions

- `IB_USER_VERBS_ABI_VERSION` set to 6.
- `IB_USER_VERBS_CMD_*` enum covering context, device/port queries, PD, AH, MR/MW, completion channel/CQ, QP, send/recv posting, multicast, SRQ, XRC-related commands, GID query, and P_Key query.
- ABI rules: no pointer types in structs, use `uint64_t` for addresses, and pad larger structures to 8-byte multiples.
- Event descriptors for async and completion events.
- Common `ib_uverbs_cmd_hdr`.
- Context and device/port/GID/P_Key query request/response structures.
- PD allocation/deallocation, with Solaris opaque PD driver output buffer.
- MR registration/deregistration.
- Completion channel creation.
- CQ create/resize/poll/notify/destroy, with WC and opaque CQ driver output buffer.
- Address vector structures: global route, AH attributes, create/destroy AH payloads.
- QP attribute, create/query/modify/destroy request/response structures, QP destination layout, and opaque QP driver output buffer.
- SGE documentation struct and send/receive WR formats.
- Post send/recv/SRQ recv payloads and bad-WR responses.
- Multicast attach/detach structures.
- SRQ create/modify/query/destroy structures and opaque SRQ driver output buffer.

## Integration Notes

This is a large ABI header used by OFED-compatible uverbs code on illumos. `ofv_resp_addr_t` from `ofa_solaris.h` models response addresses. Opaque driver output arrays are deliberately sized at 24 `uint64_t` words for PD/CQ/QP/SRQ responses.

## Risks and Gotchas

- Every field order, width, and padding choice is ABI-sensitive for 32-bit and 64-bit compatibility.
- Several command payloads contain flexible trailing arrays or driver data; handlers must validate `in_words`, `out_words`, counts, and `wqe_size`.
- XRC command IDs are listed even though this header does not define all XRC payloads here.
- The file assumes `ib_sge` packs the same across kernel/user and documents that with `ib_uverbs_sge`.
