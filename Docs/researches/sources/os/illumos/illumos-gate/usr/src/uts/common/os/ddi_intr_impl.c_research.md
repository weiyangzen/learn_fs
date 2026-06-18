# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_impl.c

## Role

`ddi_intr_impl.c` contains internal helper routines for the DDI interrupt framework. It manages per-devinfo interrupt metadata, cached supported/current interrupt information, interrupt availability limits, MSI-X bookkeeping, fixed interrupt handle tables, interrupt weight properties, obsolete busops stubs, interrupt affinity, and x86 PCI MSI/MSI-X config metadata.

## Per-Device Interrupt State

`i_ddi_intr_devi_init()` allocates `devinfo_intr_t` for a devinfo node and caches supported interrupt types. `i_ddi_intr_devi_fini()` frees the metadata only when no interrupts are currently allocated. It also frees the legacy fixed-handle table and removes any IRM request before freeing `devi_intr_p`.

The file provides straightforward getters/setters for:
- supported interrupt types;
- supported interrupt count;
- current interrupt type;
- current allocated interrupt count;
- current enabled interrupt count;
- MSI-X metadata pointer;
- fixed interrupt handle slots.

`i_ddi_get_intr_handle()` and `i_ddi_set_intr_handle()` bounds-check interrupt numbers against cached supported count. The handle table is allocated lazily when the first fixed interrupt handle is stored.

## Availability and Limits

`i_ddi_intr_get_current_navail()` returns precise IRM-managed availability when the device has a request associated with a pool and the requested type matches; it locks `ipool_navail_lock` while reading `ireq_navail`. Otherwise it falls back to `i_ddi_intr_get_limit()`.

`i_ddi_intr_get_limit()` chooses a default limit from an IRM pool when one exists or from `DDI_INTROP_NAVAIL` otherwise. It caps the result by device-supported interrupt count. If both system and driver support IRM, the limit becomes the device-supported count. Otherwise global MSI-X and MSI caps are imposed (`ddi_msix_alloc_limit` on x86 and `DDI_MAX_MSI_ALLOC` for MSI).

## Properties and Compatibility Stubs

`i_ddi_get_intr_weight()` reads the uncommitted `ddi-intr-weight` integer property and clamps values below `-1` to undefined. `i_ddi_set_intr_weight()` updates the property only for positive changed values and returns the previous weight.

The obsolete busops entry points `i_ddi_get_intrspec()`, `i_ddi_add_intrspec()`, `i_ddi_remove_intrspec()`, and `i_ddi_intr_ctlops()` all warn that the parent nexus is down-rev and return unsupported or null behavior. They exist to catch drivers/nexus paths that have not moved to the newer interrupt operation interface.

## Interrupt Affinity and x86 Metadata

`get_intr_affinity()` requires a non-null enabled interrupt handle, delegates `DDI_INTROP_GETTARGET`, and caches the returned target CPU. `set_intr_affinity()` requires an enabled MSI-X handle, delegates `DDI_INTROP_SETTARGET`, and caches the target on success.

On x86, the file also stores and retrieves PCI config handles and MSI/MSI-X capability pointers in `devinfo_intr_t`.

## Subset Relevance

This file is a lower-level support layer for interrupt resource tracking. Storage drivers depend on these helpers through the public DDI interrupt APIs, particularly for MSI/MSI-X limits, current availability, legacy fixed interrupt handles, and CPU affinity.
