# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_ndi.c

## Role

`ddi_hp_ndi.c` provides the NDI-facing hotplug interfaces used by nexus drivers and hotplug controllers. It is the companion to `ddi_hp_impl.c`: this file exposes registration, unregistration, state-change request, and connection-walk entry points, while `ddi_hp_impl.c` performs connector and port state-machine work.

## Main Entry Points

- `ndi_hp_register()` validates non-interrupt context, arguments, and nexus hotplug support, creates a `ddi_hp_cn_handle_t`, copies connection metadata, duplicates `cn_name`, initializes cached state through `ddihp_cn_getstate()`, and appends the handle to `DEVI(dip)->devi_hp_hdlp`.
- `ndi_hp_unregister()` validates context and arguments, finds the named handle, calls `ddihp_cn_unregister()`, and maps DDI return values to NDI return values.
- `ndi_hp_state_change_req()` lets a nexus/controller request a connection state transition either synchronously or asynchronously.
- `ndi_hp_walk_cn()` walks all registered connection handles for a devinfo node and invokes a caller-supplied callback with each `ddi_hp_cn_info_t`.

## Synchronous and Asynchronous Requests

For synchronous requests, `ndi_hp_state_change_req()` rejects interrupt context, locks the parent before the target devinfo node, finds the handle, and calls `ddihp_cn_req_handler()` directly. The handler deliberately does not refresh state before changing it because connector operations depend on the last known cached state to decide whether cleanup, sysevents, or probing are required.

For asynchronous requests, the function allocates a `ddi_hp_cn_async_event_entry_t` with `KM_NOSLEEP`, duplicates the connection name, holds the devinfo node, and dispatches `ddihp_cn_run_event()` to `system_taskq`. If dispatch fails, it releases the devinfo hold. The worker repeats the same parent-before-child locking discipline, finds the handle, performs the request if the handle still exists, releases the devinfo hold, and frees the event record.

## Walking Semantics

`ndi_hp_walk_cn()` holds the devinfo busy lock while walking `DEVI(dip)->devi_hp_hdlp`. It is resilient to callbacks that remove the current handle: it tracks the original head and previous node and restarts or advances appropriately when the list head or current link changes.

## Locking and Error Behavior

All public entry points reject or avoid interrupt context where needed because devinfo locking, allocation, and state transitions can block. Registration/unregistration uses `ndi_devi_enter()` on the nexus. State-change request paths use the same parent-before-child lock ordering documented in `ddi_hp_impl.c` to avoid deadlocks during nested devinfo operations.

The async path uses `KM_NOSLEEP` and taskq dispatch because it can be triggered from interrupt-adjacent hotplug notification paths. It returns `NDI_CLAIMED` once dispatched, not once the state change completes.

## Subset Relevance

This file is infrastructure for dynamic device discovery and removal. Storage and filesystem code depend on this layer indirectly when hotplug-capable buses add or remove disks, controllers, or ports.
