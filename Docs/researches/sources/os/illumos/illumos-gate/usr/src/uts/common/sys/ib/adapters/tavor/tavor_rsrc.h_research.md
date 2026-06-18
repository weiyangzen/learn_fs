# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/tavor/tavor_rsrc.h

## Purpose

Defines the Tavor resource manager interface: sleep policy, resource pool names, resource type enumeration, initialization cleanup levels, per-resource initialization descriptors, resource pool metadata, mailbox-private metadata, resource allocation handles, and public alloc/free/init/fini prototypes.

## Main Definitions

- `TAVOR_SLEEP`, `TAVOR_NOSLEEP`, and `TAVOR_SLEEPFLAG_FOR_CONTEXT()` map interrupt/panic context to non-sleeping allocation behavior.
- Named kmem caches and vmem arenas for software handles, DDR tables, mailbox pools, UAR space, and PD handles.
- `TAVOR_RSRC_NAME()` appends the driver instance to resource names; `TAVOR_RSRC_NAME_MAXLEN` bounds names.
- `tavor_rsrc_type_t`: all managed resources, including QPC, CQC, SRQC, EQC, EQPC, RDB, MCG, MPT, MTT, UAR scratch, UDAV, mailboxes, software handles, refcounts, UAR pages, and interrupt mailboxes.
- `tavor_rsrc_cleanup_level_t`: staged cleanup markers for attach/detach rollback.
- `tavor_rsrc_mbox_info_t`, `tavor_rsrc_hw_entry_info_t`, and `tavor_rsrc_sw_hdl_info_t`: initialization descriptors for mailbox, hardware-table, and software-handle resources.
- `struct tavor_rsrc_pool_info_s`: pool metadata for location, size, alignment, quantum, shift, start/DDR offset, vmem arena, soft state, and private data.
- `tavor_rsrc_priv_mbox_t`: DMA/access metadata needed to bind mailbox resources.
- `struct tavor_rsrc_s`: allocation result handle with type, address, length, index, access handle, and DMA handle.
- Prototypes for `tavor_rsrc_alloc()`, `tavor_rsrc_free()`, two-phase initialization, and cleanup.

## Integration Notes

This header underpins almost every Tavor object allocator: QPs, CQs, SRQs, EQs, memory translation tables, mailboxes, and user access regions. Consumers receive `tavor_rsrc_t` objects whose fields are only meaningful for specific resource types.

## Risks and Gotchas

- `TAVOR_SLEEPFLAG_FOR_CONTEXT()` must stay compatible with command-layer sleep flags referenced in comments.
- `TAVOR_NUM_RESOURCES` and `TAVOR_RSRC_CLEANUP_ALL` are sentinel values; new enum entries must be inserted before them.
- Resource locations distinguish DDR, system memory, and UAR memory. Misclassifying a resource affects DMA mapping, synchronization, and access-handle expectations.
- `TAVOR_RSRC_NAME()` assumes a `state` variable is in scope.
