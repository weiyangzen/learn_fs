# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddifm.c

## Role

`ddifm.c` implements DDI fault-management support for device drivers. It covers service-impact state changes, ereport posting, driver-defect ereports, FM handler registration, FM capability initialization/finalization, and access/DMA error state get/set/clear helpers.

The file defines the programming model for DDI fault-management capabilities: ereport generation, error callbacks, access-handle checking, and DMA-handle checking.

## Service Impact and Ereport Posting

`ddi_fm_service_impact()` updates devinfo service state under `devi_lock` and posts service impact ereports for lost, degraded, restored, or unaffected service. It avoids posting service changes for devices already offline.

`i_ddi_drv_ereport_post()` posts driver-defect reports from the root devinfo node when root supports ereports. In sleepable context it captures a stack trace, converts PCs to symbol strings, and includes driver name, stack depth, stack strings, and optional error-specific nvlist. In non-sleeping context it posts a smaller payload without allocating stack arrays.

`fm_dev_ereport_postv()` is the common ereport builder for DDI and NDI posting paths. It validates that the eqdip is ereport-capable, chooses normal nvlist allocation for sleepable non-panic context or reserves an errorq element for nosleep/panic-safe context, validates the required first vararg tuple is the ereport version, prefixes the error class with `io.`, generates ENA if needed, creates a dev-scheme detector FMRI from devpath/minor/devid/target-port data, merges optional payload nvlist and varargs payload, then posts via `fm_ereport_post()` or commits the errorq element.

`ddi_fm_ereport_post()` posts using the device itself as the ereport-capable node. `ndi_fm_ereport_post()` posts on behalf of a child through its parent and requires sleepable context.

## Error Callback Registration

`i_ddi_fm_handler_enter()` and `i_ddi_fm_handler_exit()` serialize driver FM error handling through the FM handle mutex and record the lock owner. `i_ddi_fm_handler_owned()` checks ownership.

`ddi_fm_handler_register()` rejects interrupt context, finds the parent devinfo node, verifies both child and parent have error-callback capability, allocates an error handler record and target record, and links it into the parent's FM target list under the parent's FM handler lock.

`ddi_fm_handler_unregister()` performs the inverse search/removal from the parent target list and frees the records.

## FM Initialization and Finalization

`ddi_fm_init()` must be called while the device is attaching. It honors default capability requests, asks the parent bus to initialize FM support and possibly adjust the iblock cookie, allocates an `i_ddi_fmhdl`, creates a virtual kstat named `fm`, initializes error counters and locks, and then enables the subset of requested capabilities also supported by the parent/system.

For enabled capabilities it creates devinfo properties:
- `fm-ereport-capable`;
- `fm-errcb-capable`;
- `fm-dmachk-capable`;
- `fm-accchk-capable`.

It also initializes DMA and access error caches through `i_ndi_fmc_create()` and returns the actual capability bitmask and iblock cookie.

`ddi_fm_fini()` requires detach or attach cleanup context. It deletes the kstat, removes capability properties, unregisters error callbacks for non-root devices, destroys DMA/access caches, calls parent bus FM fini, frees the handle, and clears `devi_fmhdl`. The access property removal string is `fm-accachk-capable`, which differs from the creation string `fm-accchk-capable` and is notable when auditing property cleanup behavior.

`ddi_fm_capable()` returns the device's current FM capability bitmask or `DDI_FM_NOT_CAPABLE`.

## Access and DMA Error Helpers

`ddi_fm_acc_err_get()` and `ddi_fm_dma_err_get()` validate the caller version, return early for null handles, and copy error status, ENA, expected flag, and handle pointer into `ddi_fm_error_t` when an error exists. Invalid versions generate driver-defect ereports and panic.

`ddi_fm_acc_err_clear()` and `ddi_fm_dma_err_clear()` reset handle error state to `DDI_FM_OK`, zero ENA, and mark the next error unexpected. Invalid versions also panic through defect reporting.

`i_ddi_fm_acc_err_set()` and `i_ddi_fm_dma_err_set()` set ENA/status/expected fields on the handle and increment per-device FM kstat counters for access or DMA errors.

`i_ddi_fm_acc_err_cf_get()` and `i_ddi_fm_dma_err_cf_get()` return comparison metadata from the handle's error record.

## Subset Relevance

Fault management is central to robust storage and filesystem operation because it records device faults, DMA/access errors, and service degradation. Storage drivers use these facilities to communicate hardware and I/O failures to the broader fault-management stack.
