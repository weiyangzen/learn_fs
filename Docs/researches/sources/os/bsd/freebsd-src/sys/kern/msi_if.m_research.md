# File Research: sources/os/bsd/freebsd-src/sys/kern/msi_if.m

## Purpose
Declares the kobj interface for MSI/MSI-X interrupt allocation, release, mapping, and optional IOMMU-domain setup. This is bus/controller glue used by interrupt controller and PCI/MSI providers.

## Methods
- `alloc_msi()` allocates a vector group for a child device with requested and maximum counts.
- `release_msi()` releases a vector group.
- `alloc_msix()` allocates a single MSI-X interrupt source.
- `release_msix()` releases a single MSI-X interrupt source.
- `map_msi()` produces the MSI message address/data pair for an interrupt source.
- `iommu_init()` optionally initializes an IOMMU domain for MSI remapping.
- `iommu_deinit()` tears down optional MSI IOMMU state.

## Defaults
The default `iommu_init()` sets the domain pointer to `NULL` and succeeds. The default `iommu_deinit()` is a no-op. Allocation, release, and mapping methods have no defaults here and must be supplied by implementations.

## Dependencies
The interface imports `<machine/bus.h>`, `<dev/iommu/iommu_msi.h>`, and forward-declares `struct intr_irqsrc`. It is intended for device/bus interrupt plumbing rather than process or filesystem code.

## Filesystem / VM Relevance
There is no direct filesystem behavior. Indirectly, storage and filesystem devices using MSI/MSI-X depend on this interrupt allocation path for device operation, and IOMMU MSI remapping can affect DMA/interrupt isolation.
