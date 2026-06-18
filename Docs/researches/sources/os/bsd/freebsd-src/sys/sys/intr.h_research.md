# File Research: sources/os/bsd/freebsd-src/sys/sys/intr.h

INTRNG-only interrupt-controller interface for mapping platform interrupt descriptions to interrupt sources. It includes machine interrupt definitions and rejects builds without `INTRNG`.

Defines map-data types for ACPI, FDT, GPIO, MSI, and platform-specific mappings, plus `struct intr_irqsrc` for registered interrupt sources with device, IRQ id, flags, name, CPU mask, counter, handler count, event, optional solo filter, and MSI IOMMU data.

Exports PIC registration/root claiming, interrupt source registration/dispatch, IRQ resource activation/setup/teardown/description, map/unmap/clone, MSI/MSI-X allocation/release/mapping, SMP IRQ binding and secondary PIC init, IPI registration/setup/send/dispatch, and the main assembly-facing interrupt entrypoint.
