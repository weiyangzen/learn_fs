# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ctfs/ctfs_event.c

## Purpose

`ctfs_event.c` implements ctfs event endpoints: per-contract `events` files and per-type `bundle`/`pbundle` files. These files expose contract event queues through ioctl and poll operations.

## File Shape

- Size: 498 lines, 12,022 bytes.
- SHA-256: `6a060ecae6a9ff0cd2f054d3bb2efa297a0845f01735dc6c64624cac72341f78`.
- Public creators: `ctfs_create_evnode()`, `ctfs_create_pbundle()`, and `ctfs_create_bundle()`.
- Operation vectors: `ctfs_tops_event` and `ctfs_tops_bundle`.

## Core Behavior

- `ctfs_endpoint_open()` validates read-only large-file open flags with optional `FNONBLOCK`, initializes the endpoint listener once, records nonblocking mode, and adds the listener to the target contract event queue.
- `ctfs_endpoint_inactive()` removes active listeners and cleans poll state.
- `ctfs_endpoint_ioctl()` handles `CT_ERESET`, `CT_ERECV`, `CT_ECRECV`, `CT_ENEXT`, and `CT_ERELIABLE` using common contract event queue listener helpers. It passes zone unique ID and optional receive credential checks.
- `ctfs_endpoint_poll()` reports `POLLIN` when the listener has a current position, otherwise returns a pollhead for wakeup.
- Per-contract `events` nodes require `secpolicy_contract_observer()` for access/open and attach to the contract's `ct_events` queue.
- Bundle nodes attach to either the type-wide bundle queue or the current process's process-bundle queue. Bundle ioctl receive privilege checking is enabled for ordinary bundle queues and skipped for process-bundle queues as encoded by the queue list number.
- Inactive handlers hold the parent vnode while tearing down endpoint listeners, preventing destruction order issues with active listeners.

## Dependencies And Contracts

- Uses contract event queue APIs: `cte_add_listener()`, `cte_remove_listener()`, `cte_reset_listener()`, `cte_get_event()`, `cte_next_event()`, and `cte_set_reliable()`.
- Uses pollhead state embedded in endpoint listeners.
- Uses contract type bundle accessors `contract_type_bundle()` and `contract_type_pbundle()`.

## Maintenance Notes

Endpoint setup is one-shot per vnode instance; the code assumes bundle nodes are opened immediately after lookup rather than cloned on open. Listener cleanup ordering is important because contracts must not be destroyed while listeners remain attached.
