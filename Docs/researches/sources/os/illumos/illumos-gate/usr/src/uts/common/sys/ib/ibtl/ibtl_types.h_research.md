# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibtl_types.h

## Purpose

`ibtl_types.h` defines the common IBTL data types shared by IBTI clients and IBCI/HCA drivers. It is the core ABI/type catalog for handles, endian conversion, HCA and port attributes, channel state, memory registration, work requests, completions, asynchronous events, and RDMA IP addressing.

## Main Types

The header defines opaque handles for clients, HCAs, channels, SRQs, CQs, services, service bindings, FMR pools, memory areas, PDs, CQ schedulers, MRs, MWs, UD destinations, address handles, EEC/RD destinations, IO memory allocations, and memory IOV maps.

It defines endian conversion macros, key and work-request ID types, selector/rate/lifetime request types, channel/SRQ queue sizing, execution modes, allocation flags for MW/PD/UD/SRQ/L_Key, retry/timer enums, HCA capability flags, page-size masks, and `ibt_hca_attr_t`, which is the large static capability descriptor for HCA limits, memory features, CQ moderation, firmware version, XRC, WQE sizing, RSS, FC offload, and device info.

## Port and Channel Data

`ibt_hca_portinfo_t` describes cached/queryable port state including LID, violation counters, SM data, link state, width/speed, SGID/P_Key tables, default P_Key index, virtual lanes, subnet timeout, capabilities, and max message size. `ibt_adds_vect_t` and `ibt_cep_path_t` describe addressing and connected endpoint paths.

Channel-related types include RSS attributes, migration state, transport service IDs, CEP states, attribute flags, CEP control and modify flags, CQ notification/scheduling/attributes, and handler attributes.

## Memory and Work Requests

The memory section defines MR flags, MR query flags, physical buffers, MR/PMR descriptors, MR/PMR/DMR/SMR attributes, IOV mapping attributes, key state, MR/MW query attributes, synchronization ranges, VA translation attributes, and FMR pool attributes.

Work request definitions cover opcodes, completion flags/detail bits, `ibt_wc_t`, WR flags, memory-window bind, SGL data segments, atomic/RDMA/fast-register/local-invalidate operations, raw transport placeholders, RC/UC/RD/UD/LSO send payloads, Fibre Channel over IB WR payloads, `ibt_send_wr_t`, `ibt_recv_wr_t`, and the union `ibt_all_wr_t`.

## Events and Miscellaneous

The file defines asynchronous event codes for channel, CQ, port, HCA attach/detach, SRQ, port-change, client reregister, and FEXCH errors; port-change flags; FC syndromes; CI private data flags; object type identifiers; MR private callback data; memory error payloads; failure classification; and `ibt_ip_addr_t` for IPv4/IPv6 RDMA IP CM support.

## Research Notes

This is the most important structural header in the group. Storage-relevant consumers depend on these exact memory-registration, work-request, CQ, and completion structures for RDMA data paths. The file also exposes several illumos-specific extensions for RSS, LSO, FMR, reserved L_Key, DMA MR, memory-management extensions, and Fibre Channel offload.
