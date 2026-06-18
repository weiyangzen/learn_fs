# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/rsm/rsm_in.h

## Role

`rsm_in.h` defines internal kernel-agent state for RSM resources, import sharing, resource tables, hash tables, IPC slots, importer tracking, and DR/path-related state.

## Driver and Resource State

The header sets driver constants such as minor number, controller count, IPC queue sizes, service ID, queue size, max segments, max nodes, and max controllers.

`rsm_driver_data` tracks driver state, dynamic reconfiguration callbacks, and synchronization. Driver states cover new, OK, pre/post-delete, DR, registration, and unregistration processing.

`rsm_resource_state_t` models export/import lifecycle states from new/bind/export/connect/mapping/active through quiesce, disconnect, zombie, and abort states. `rsm_resource_type_t` distinguishes export segment, import segment, and barrier resources.

## Segment Model

`rsmresource_t` is the common resource header. `rsmseg_t` embeds it and adds owner IDs, length, region list, flags, poll state, condition variable, NIC segment ID, ACLs, pollhead, devmap cookies, mapinfo, RSMPI handles, umem cookie, shared-import pointer, RDMA count, and process pointer.

`rsm_import_share_t` tracks shared importers for a node/segment: state, refcounts, map counts, mode/owner, mapinfo, flags, and connect cookie.

## Tables and Messaging

The file defines:
- block-based resource table roots.
- hash tables guarded by rwlocks.
- IPC slots with flags/cookie/data and condition variables.
- IPC descriptor with fixed slot array.
- importing and republish tokens.
- list heads/elements for suspend acknowledgements and node-dead state.

## Research Notes

This is an internal state-machine header. Correctness depends on lock macros, resource state transitions, shared-import refcount/mapcount handling, and IPC slot cookie sequencing.
