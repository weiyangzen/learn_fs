# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_ci_types.h

## Purpose

`ibtl_ci_types.h` contains types and compatibility mappings shared by IBTL and the CI/HCA driver interface. It bridges public channel terminology to lower-level QP/AH/EEC terminology and exposes selected structures to avoid data copying in fast paths.

## Main Content

The header maps opaque fields and status names between QP/address-handle language and channel/UD-destination language. It defines CI-specific aliases for address-vector fields, work-completion fields, multicast LID, HCA QP capability names, and CEP timeout storage.

`ibt_ud_dest_t` is shared between IBTL and CI so UD send processing can directly consume address handle, destination QPN, and Q_Key without copying. `ibt_rd_dest_t`, RD transport types, and EEC structures are reserved or legacy-oriented.

The file defines QP types, special QP types, QP allocation flags, `ibt_qp_alloc_attr_t`, QP transport-specific query/modify structures for RC/UC/RD/UD, common `ibt_qp_info_t`, `ibt_qp_query_attr_t`, and EEC query/modify structures.

## Research Notes

This is a compatibility and performance boundary header. It lets CI drivers implement traditional QP verbs while IBTI clients can use the higher-level channel API. The shared `ibt_ud_dest_t` layout is especially important because it is directly referenced by HCA drivers during UD work-request processing.
