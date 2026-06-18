# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_intr.c

## Purpose
Implements FreeBSD's new-style interrupt framework: interrupt controller registration, interrupt source registration, resource-to-source mapping, activation/setup/teardown, MSI/MSI-X support, counters, CPU binding, IPI support, and DDB inspection.

## Key Elements
- Root controller slots: `intr_irq_roots`.
- Controller registry: `struct intr_pic`, `pic_list`.
- Interrupt sources: global `irq_sources`, `intr_isrc_register()`, `intr_isrc_deregister()`.
- Dispatch: `intr_irq_handler()`, `intr_isrc_dispatch()`, `intr_child_irq_handler()`.
- Resource operations: `intr_activate_irq()`, `intr_deactivate_irq()`, `intr_setup_irq()`, `intr_teardown_irq()`, `intr_describe_irq()`.
- CPU binding: `intr_bind_irq()`, `intr_irq_next_cpu()`, SMP shuffle.
- MSI/MSI-X: `intr_msi_register()`, `intr_alloc_msi()`, `intr_release_msi()`, `intr_alloc_msix()`, `intr_release_msix()`, `intr_map_msi()`.
- Mapping table: `intr_map_irq()`, `intr_unmap_irq()`, `intr_map_clone_irq()`.
- SMP IPI support: `intr_ipi_pic_register()`, `intr_ipi_setup()`, `intr_ipi_send()`, `intr_ipi_dispatch()`.
- DDB command: `show irqs`.

## Behavior
Initialization allocates interrupt counters/names, a bitmap for counter allocation, and the IRQ source table. Non-IPI interrupt sources get two counters: handled and stray. Dispatch increments the handled counter, invokes either a solo filter or MI `intr_event`, and increments the stray counter on failure.

PICs and MSI controllers are registered in a shared controller list with type flags. Root PICs claim a root slot with a low-level filter. Interrupt resources are mapped through `intr_map_irq()`, resolved through the PIC or MSI map data, activated by `PIC_ACTIVATE_INTR`, and then set up with event handlers and PIC enable/setup calls.

MSI allocation asks the MSI controller for interrupt sources, attaches optional IOMMU domains, creates MSI map data, and returns framework IRQ resource IDs. Mapping MSI vectors calls `MSI_MAP_MSI()` and translates MSI addresses through IOMMU when present.

## Research Notes
There are two tables with different meanings: `irq_sources` maps framework IRQ source numbers to `intr_irqsrc`, while `irq_map` maps bus resource IDs to PIC/MSI map data and active sources. The map table is fixed at `2 * intr_nirq` and currently panics rather than expanding.
