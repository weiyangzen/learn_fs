# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr.c

## Role

`ddi_intr.c` implements the public DDI interrupt framework and legacy interrupt compatibility APIs. It covers hardware interrupt discovery, allocation/free, capabilities, priority, handler registration, MSI-X handler duplication, enable/disable, MSI block enable/disable, masking, pending-status queries, IRM request resizing, soft interrupts, and older `ddi_add_intr()`/`ddi_remove_intr()` style interfaces.

The file is the primary consumer-facing interrupt API layer. Platform and nexus-specific work is delegated through `i_ddi_intr_ops()` and internal helpers implemented elsewhere.

## Interrupt Discovery and Allocation

`ddi_intr_get_supported_types()`, `ddi_intr_get_nintrs()`, and `ddi_intr_get_navail()` validate inputs, consult cached devinfo interrupt metadata when present, and otherwise issue nexus interrupt operations for supported types, count, or availability.

`ddi_intr_alloc()` performs the central allocation workflow:
- validates handles, type, count, interrupt number, and allocation behavior;
- prevents fixed-interrupt duplicate allocation for the same `inum`;
- obtains supported interrupt count and current interrupt type/count;
- enforces one interrupt type per device at a time;
- enforces device-supported limits and MSI power-of-two count rules;
- initializes per-device interrupt state and inserts the device into IRM on first allocation;
- adjusts IRM reservations for non-IRM-aware drivers on later allocations;
- applies strict versus normal allocation behavior when requested count exceeds available count;
- delegates allocation, priority lookup, and capability lookup to `i_ddi_intr_ops()`;
- records current type, supported count, and current allocated count;
- allocates one `ddi_intr_handle_impl_t` per actual interrupt, initializes its rwlock and fields, allocates a private handle, and stores fixed interrupt handles for legacy lookup.

On allocation failure after nexus allocation, the fail path frees the nexus allocation and finalizes per-device interrupt state.

## Free, Capabilities, and Priority

`ddi_intr_free()` requires an allocated handle, except duplicated MSI-X handles are freed from `ADDED` state. It delegates `DDI_INTROP_FREE`, updates duplicate counts or current interrupt counts, adjusts IRM for non-aware drivers, clears fixed-interrupt handle slots, finalizes devinfo interrupt state, frees private handles, destroys the rwlock, and releases the handle memory.

`ddi_intr_get_cap()` returns cached capabilities or asks the nexus, hiding `DDI_INTR_FLAG_MSI64` from consumers. `ddi_intr_set_cap()` only allows level/edge capability changes while the handle is allocated and supported.

`ddi_intr_get_hilevel_pri()` returns `LOCK_LEVEL + 1`. `ddi_intr_get_pri()` returns cached priority or queries the nexus. `ddi_intr_set_pri()` validates range, requires allocated state, avoids no-op changes, calls the nexus, and caches the new priority.

## Handler and Enable Lifecycle

`ddi_intr_add_handler()` requires an allocated handle and non-null callback, stores callback fields, delegates `DDI_INTROP_ADDISR`, and transitions to `ADDED`. On failure it clears callback state.

`ddi_intr_dup_handler()` supports MSI-X duplicate vectors only. It verifies the original handle is not merely allocated, is MSI-X, and is not itself a duplicate, asks the nexus to duplicate the vector, allocates a new handle, copies the original, reinitializes the duplicate's lock and unique fields, marks it `DDI_INTR_MSIX_DUP`, and points back to the original.

`ddi_intr_remove_handler()` requires `ADDED` state. Duplicates skip nexus ISR removal because the original owns the ISR. Originals must have zero duplicate count before `DDI_INTROP_REMISR`; successful removal clears callback fields and returns to allocated state.

`ddi_intr_enable()` and `ddi_intr_disable()` require added/enabled states respectively, reject per-vector enable/disable for block-capable MSI handles, verify MSI-X handle correctness, issue nexus operations, and maintain per-device enabled counts.

`ddi_intr_block_enable()` and `ddi_intr_block_disable()` validate every handle in the array for MSI block capability and consistent state, then issue one block operation via the first handle and update all handle states. The enabled count is treated as one block enable for the device.

## Masking, Pending, IRM, and Soft Interrupts

`ddi_intr_set_mask()`, `ddi_intr_clr_mask()`, and `ddi_intr_get_pending()` require the relevant capability bits and delegate to nexus operations.

`ddi_intr_set_nreq()` lets IRM-aware drivers change the number of requested interrupts. It requires an active interrupt type, IRM support for that type, and a request not exceeding supported interrupt count, then calls `i_ddi_irm_modify()`.

Soft interrupt APIs allocate `ddi_softint_hdl_impl_t` records, validate soft priority ranges, delegate platform add/remove/trigger/set-priority operations, and expose get/set/trigger wrappers. Legacy soft interrupt APIs translate older priority preferences into modern soft interrupt handles.

## Legacy Compatibility

The obsolete API section adapts old fixed-interrupt interfaces to the new framework:
- `ddi_intr_hilevel()` allocates or reuses a fixed interrupt handle and compares priority to high-level threshold.
- `ddi_dev_nintrs()` returns fixed interrupt count.
- `ddi_get_iblock_cookie()` returns priority as an iblock cookie.
- `ddi_add_intr()` allocates one fixed interrupt, retrieves priority, adds a handler, enables it, fills legacy cookies, and frees the temporary handle array.
- `ddi_remove_intr()` finds a fixed interrupt handle, disables it, removes the handler, and frees it.
- `ddi_add_fastintr()` is unsupported.
- old soft interrupt functions allocate/remove/trigger modern soft interrupt handles behind legacy opaque IDs.

## Subset Relevance

Interrupt allocation and teardown are fundamental to storage controllers, block devices, and filesystem-adjacent device drivers. This file defines the driver-facing contract for interrupt resources and directly interacts with IRM, making it part of the OS/storage substrate covered by subset A.
