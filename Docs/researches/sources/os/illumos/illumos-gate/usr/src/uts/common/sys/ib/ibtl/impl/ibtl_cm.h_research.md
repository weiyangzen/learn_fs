# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/ibtl/impl/ibtl_cm.h

## Purpose

`impl/ibtl_cm.h` defines the private interface between IBTL and the InfiniBand Communication Manager. It supports CM private data attachment, local port/GID discovery, RC QP lifetime coordination, service-count tracking, cached port queries, active port selection, subnet notice delivery, and node-info callbacks.

## Main Interfaces

The header aliases `ibt_ud_dest_t`’s opaque field as `ud_dest_hca` for CM use. It declares functions to set, get, release, and wait on per-channel CM private data.

`ibtl_cm_hca_port_t` packages HCA GUID, port GUID, base LID, port number, SGID index, LMC, and MTU for a source GID. Lookup functions retrieve HCA/port information, companion GIDs, MultiSM state, first full P_Key index, and cached HCA portinfo.

## RC Lifetime Coordination

The `ibtl_cm_chan_is_*` functions tell IBTL when an RC channel is opening, open, aborted, closing, closed, reused, or already in closing/closed state. These exist to coordinate QPN reuse and TIMEWAIT behavior between CM and client-driven free paths.

## Port Lists and Notices

`ibtl_cm_port_list_t` describes active source ports for path selection, including HCA GUID, SGID, base LID, MTU, SGID index, port number, MultiSM flags, SAA handle, and source IP. The header also declares subnet notice registration/delivery helpers and an initialization-failure payload containing failing SGIDs.

## Research Notes

This header exposes the hidden cooperation needed between path lookup, CM state machines, and IBTL resource lifetime. For RC storage transports, the QPN reuse/TIMEWAIT hooks are the key safety mechanism.
