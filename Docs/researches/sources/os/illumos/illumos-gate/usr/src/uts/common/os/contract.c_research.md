# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/contract.c

This file implements the core Solaris/illumos contracts framework. Contract types provide resource-specific behavior, while this file handles common contract identity, ownership, reference counts, templates, type registration, global/type/process lookup, event queues, listeners, visibility, and event delivery.

Core behavior:
- `contract_init()` creates the global ID space and AVL tree, initializes process and device contract types, and initializes process 0 contract state.
- `contract_ctor()` initializes a new contract, allocates an ID, creates its per-contract event queue, tests/increments `project.max-contracts`, inserts the contract into owner, global, and type AVL namespaces, and stores it as the LWP’s latest contract for that type.
- `contract_rele()` drops a reference; the last release removes the contract from global/type trees, frees its ID, decrements project contract accounting, destroys common state, and calls the type-specific free op.
- `contract_hold()`, `contract_getzuniqid()`, and `contract_setzuniqid()` provide reference and zone-unique-id helpers.
- `contract_abandon()` removes ownership, optionally inherits to a regent process contract when terms allow it, calls type-specific abandon when not inherited, trims the old process bundle queue, and drops references.
- `contract_adopt()` lets a process adopt an inherited contract from its process contract, transfers ownership, inserts it into `p_ct_held`, and copies critical events to the new owner’s process bundle queue.
- `contract_ack()`, `contract_qack()`, and invalid/notsupported helpers handle critical and negotiation event acknowledgements and delegate negotiation-specific ACK/NACK/QACK to type operations.
- `contract_orphan()` marks a contract orphaned and ACKs all outstanding critical events.
- `contract_destroy()` marks a contract dead, drains its contract event queue, trims type bundles, calls type-specific destroy, and releases the owner reference.
- Contract vnode helpers track ctfs vnodes associated with contract directories without holding permanent vnode references.
- `contract_exit()` abandons all contracts held by an exiting process and drains process bundle queues.
- `contract_status_common()` fills common `ct_status` fields, including zone virtualization of holder/state visibility.
- `contract_owned()` and `contract_checkcred()` implement event visibility by owner, creator zone/uid, effective zone, and observer privilege rules.
- `contract_type_init()`, `contract_type_count()`, `contract_type_max()`, `contract_max()`, lookup, pointer, time, bundle, and process-bundle helpers expose type/global indexing and queue allocation.
- `ctparam_copyin()` and `ctparam_copyout()` copy contract parameter ioctl payloads safely outside process-lock regions.
- Template helpers initialize, copy, duplicate, free, set/get common terms, activate/clear active LWP templates, and invoke type-specific create/set/get/free operations.
- Event queue internals manage queue creation/destruction, event holds/releases, listener movement, queue reference releases, credential checks, readable-event selection, tail-listener wakeups, event copying, trimming, draining, publishing, and reliable delivery.
- `cte_publish_all()` initializes an event, assigns an event ID, holds the generating contract, delivers the event in contract queue, type bundle queue, and owner process bundle queue order, and serializes per-contract delivery with `ct_evtlock`.
- Listener APIs add/remove/reset listeners, advance past an event, read/copy out events and nvlist payloads, and enable reliable delivery with `PRIV_CONTRACT_EVENT`.

Important invariants:
- Lock order is explicitly documented: `ct_evtlock`, regent `ct_lock`, member `ct_lock`, `pidlock`, `p_lock`, queue locks/`contract_lock`, `cte_lock`, then `ct_reflock`.
- Global contract lists do not own references; contracts are removed from namespaces atomically with last-reference release.
- A contract is owned by a process, inherited by a regent process contract, orphaned, or dead; `ct_owner`/`ct_regent` are protected by `ct_lock`, while holder AVL linkage is protected by the holder lock.
- Event references include queue holds, listener queue-position references, copyout holds, and the event’s hold on the generating contract.
- Process bundle queues are dynamically allocated and refcount-like through `CTQ_REFFED`; they can outlive the process if listeners remain.
- `cte_trim()` removes informative/ACKed events only when unreferenced or marks contract-specific events trimmed until reliable readers release them.
- `cte_get_event()` holds the event while copying to userland and uses `CTLF_COPYOUT`/`CTLF_RESET` to avoid racing listener movement/reset with partial copyout.
- Critical events increment `ct_evcnt` until ACKed; orphan/dead paths must clear or ACK outstanding critical events.
- Zone visibility uses both creator-zone unique ID and mutable effective-zone unique ID for global-zone-created contracts visible in non-global zones.
