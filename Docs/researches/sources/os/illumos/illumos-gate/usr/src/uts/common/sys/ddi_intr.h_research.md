# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr.h

This is the public DDI interrupt interface header for kernel drivers. It defines interrupt return conventions, interrupt types, priorities, capability flags, opaque interrupt handles, handler typedefs, allocation behavior flags, and both modern and legacy interrupt APIs.

The modern interrupt model supports fixed, MSI, and MSI-X interrupts through `DDI_INTR_TYPE_FIXED`, `DDI_INTR_TYPE_MSI`, and `DDI_INTR_TYPE_MSIX`. Drivers query supported types, number of interrupts, available interrupts, allocate/free handle arrays, query/set capabilities, query/set priority, add/duplicate/remove handlers, enable/disable individual or block interrupts, mask/unmask interrupts, query pending state, and set requested interrupt count.

Soft interrupt support uses `ddi_softint_handle_t` plus `ddi_intr_add_softint`, remove, trigger, and priority get/set calls. Priority constants distinguish hardware priority ranges from soft interrupt preferences.

The file includes `ddi_intr_impl.h` when `_KERNEL` is set, so public handle declarations are paired with private implementation layout for kernel consumers. Legacy APIs are retained for older drivers: `ddi_intr_hilevel`, `ddi_get_iblock_cookie`, `ddi_dev_nintrs`, `ddi_add_intr`, `ddi_add_fastintr`, `ddi_remove_intr`, and older softintr routines.

Research notes:
- Return values `DDI_INTR_CLAIMED` and `DDI_INTR_UNCLAIMED` are the ISR contract.
- New code should prefer the `ddi_intr_*` handle-based APIs over legacy `ddi_add_intr`/`ddi_add_fastintr`.
- MSI-X handler duplication and block enable behavior are backed by private state in `ddi_intr_impl.h`.
