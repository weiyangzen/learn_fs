# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/daplt/daplt.h

## Purpose

Defines the kernel-side state and resource objects for the `daplt` uDAPL kernel agent: HCA inventory, per-instance state, generic hash tables, IA/PD/EVD/EP/MR/MW/SP/CNO/SRQ resources, connection event bookkeeping, shared MR tracking, and a resource table.

## Main Definitions

- Driver version, taskq size, and attached/detached status constants.
- `daplka_hca_t`: HCA GUID/handle/attributes/ports, resource counters, refcount, and linked-list membership.
- `daplka_t`: per-device instance state with mutex, devinfo, IBT client handle, HCA list, and status.
- Generic hash table types with table and key locks plus optional free/lookup callbacks.
- `daplka_resource_t`: common header for all resources, including type, resource number, refcount, charge flag, and free callback.
- Hash table sizes for EP, MR, MW, PD, SP, EVD, global SP, timers, CNO, and SRQ.
- IA state machine for races between MW allocation and MR cleanup callbacks.
- Resource structs for:
  - IA with per-IA resource hash tables and async EVD list.
  - PD with HCA and IBT PD handle.
  - EVD with CQ handle, event queues, waiters, cookie, and optional CNO.
  - SRQ with PD/HCA association and real size.
  - EP with channel handle, EVDs, PD/SRQ, state, timer, passive cookie, private data, and GIDs.
  - MR/MW with IBT handles and locking.
  - SP with service/bind handles and connection backlog.
  - CNO with wait condition and EVD cookie.
  - Shared MR AVL entries.
- Resource table block/root structures for minor-resource mapping.

## Integration Notes

This is the private kernel representation behind the ioctl ABI in `daplt_if.h`. It maps user-visible hash keys and cookies to IBT resources and tracks ownership/refcounts inside the kernel driver.

## Risks and Gotchas

- Many objects are documented as scheme-protected rather than solely lock-protected; correctness depends on higher-level DAPL lifecycle rules.
- IA MW freeze states handle a specific race between MR cleanup and MW allocation.
- Passive connection cookies encode timestamp plus backlog index; consumers must validate backlog state, not just decode the index.
- EVD event queues mix asynchronous, connection-request, and connection events under one lock.
