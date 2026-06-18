# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/ibti_common.h

## Purpose

`ibti_common.h` defines shared public IBTI types and prototypes used by clients across HCA discovery, path lookup, connection management, service registration, completion queues, memory registration, multicast, protection domains, SRQs, FMR, IP path resolution, and private contract interfaces.

## Main Types

The file defines the IBTI version, client classes, client module registration structure, async and memory callbacks, subnet notice callbacks, service-data masks, path request/response structures, alternate path structures, RC open arguments/returns, UD SIDR destination/return structures, multicast attributes/results, service descriptors/bindings, property update payloads, node information, IP path/source-IP structures, RDMA IP CM private data, address records, and partition attributes.

Client classes distinguish storage, network, generic, user, IBMA, CM, DM, and related management clients. `ibt_clnt_modinfo_t` is the persistent registration descriptor passed to `ibt_attach()`.

## Function Surface

The header declares client attach/detach, HCA listing/open/close/query/port query/private data helpers, path and alternate-path lookup, RC open/close/prime-close/recycle, UD recycle, channel queue and RDMA modification, service registration and binding, CM delay/proceed, CQ allocation/free/notification/handler/poll/query/resize/modification, memory registration/reregistration/shared registration/synchronization, memory windows, L_Key allocation, physical/DMA memory registration, address translation, work request posting, path migration, multicast join/leave/query/attach/detach, subnet notices, PD allocation/free, P_Key conversions, CI private data exchange, node lookup, reprobe, SRQ lifecycle, failure classification, hardware presence check, FMR pool operations, IP path/source-IP lookup, RDMA IP SID formatting/parsing, private Address Record APIs, HCA system-image and port modification, IO memory allocation, partition attribute callbacks, and LID-to-node lookup.

`ibt_get_alt_path()` is declared in both the connection and alternate path sections, reflecting header organization rather than a separate API.

## Research Notes

This is the broadest public IBTF interface header in the group. For filesystem and storage research, the important areas are client classing for `IBT_STORAGE_DEV`, RC channel open/close semantics, memory registration APIs for RDMA buffers, CQ completion delivery, FMR/physical registration, and IP path helpers used by RDMA-aware upper-layer protocols.
