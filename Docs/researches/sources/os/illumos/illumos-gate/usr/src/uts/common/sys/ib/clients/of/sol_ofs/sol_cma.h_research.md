# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_cma.h

This Solaris-specific CMA private header defines the in-kernel state behind `rdma_cm_id` for the illumos OpenFabrics RDMA-CM implementation.

Core definitions:
- Macros classify UDP/IPoIB IDs and valid IPv4/IPv6 socket addresses.
- Global listen records track service IDs, client/service handles, and CMID channel lists.
- `cma_chan_state_t` models RDMA-CM ID progression through idle, bound, address/route query, resolved, event-notified, connect/listen/disconnect/accept/reject, destroying, HCA down, and port down states.
- Listen metadata distinguishes root listener CMIDs from endpoint CMIDs and stores root/endpoint list entries plus IBTF service/bind handles.
- Client/server role state is tracked separately through `sol_cma_connect_flag_t` and `cma_req_cmid_state_t`.

Main structure:
- `sol_cma_chan_t` embeds `struct rdma_cm_id` first, then adds request/accepted AVL trees, counters, state, mutex/CV, transport type, IB/iWARP client handles, QP handle, listen metadata, connection params, session/QP metadata, and transport-specific `ibcma_chan_t`.

Important helpers:
- `sol_cma_any_addr()` recognizes wildcard IPv4/IPv6 addresses.
- `cma_create_new_id()` clones route/address/device/listen-root state for derived IDs.
- `cma_get_req_idp()` and `cma_get_acpt_idp()` search listener AVL trees and require the root channel mutex.

Risk-sensitive invariants:
- `struct rdma_cm_id` must remain the first field of `sol_cma_chan_t` for casting.
- Request and accepted CMID AVL trees are protected by the root channel mutex.
- Destroy/event/API progress bits coordinate caller-facing destruction with async callbacks.
