# File Research: sources/virtualization/qemu/hw/virtio/virtio-pci.c

## Purpose
Core QEMU virtio-over-PCI transport implementation. It exposes a `VirtIOPCIProxy` PCI device that owns a `VirtioBusState`, maps legacy and modern virtio PCI regions, handles PCI/MSI-X interrupt routing, migration state, ioeventfd/irqfd acceleration, reset, QOM type registration, and virtio bus callbacks.

## Main Responsibilities
- Implements legacy virtio PCI I/O BAR behavior: feature negotiation, queue PFN/address, queue select/notify, status, ISR, and MSI-X vector access (`virtio_ioport_write`, `virtio_ioport_read`, `virtio_pci_config_read/write`).
- Implements modern virtio PCI capabilities and regions: common config, ISR, device config, notify MMIO, optional notify PIO, and PCI CFG access capability.
- Bridges virtio bus callbacks to PCI transport behavior: notify, save/load config, save/load queue vectors, guest notifier setup, ioeventfd assignment, DMA address space lookup, IOMMU detection, and queue enabled state.
- Manages MSI-X vector usage and KVM irqfd routing for virtqueues and config interrupts.
- Registers generic, transitional, and non-transitional virtio PCI QOM types from `VirtioPCIDeviceTypeInfo`.

## Key Data and State
- `VirtIOPCIProxy` holds PCI device state, embedded virtio PCI bus, feature selectors (`dfselect`, `gfselect`), selected guest features, modern queue state array, BAR indices, modern region metadata, MSI-X vector count, and optional irqfd vector bookkeeping.
- `VirtIOPCIQueue` migration state stores queue size, enabled flag, descriptor/avail/used addresses, and runtime reset state for modern queues.
- `virtio_pci_id_info[]` maps virtio device IDs to legacy transitional PCI device IDs and PCI class IDs for selected device types.

## Initialization and Device Plug Flow
- `virtio_pci_realize()` sets default BAR layout: legacy I/O BAR 0, MSI-X BAR 1, optional modern PIO BAR 2, modern 64-bit memory BAR 4/5. It initializes modern region offsets and sizes, resolves `disable-legacy` auto behavior, initializes PCIe capabilities if needed, creates the virtio-pci bus, then delegates subclass realization.
- `virtio_pci_pre_plugged()` adds `VIRTIO_F_VERSION_1` for modern transport and always adds `VIRTIO_F_BAD_FEATURE`.
- `virtio_pci_device_plugged()` validates legacy/modern compatibility, sets PCI IDs/class/revision, maps modern capability regions when enabled, initializes MSI-X, installs PCI config read/write hooks, registers legacy BAR when needed, and initializes SR-IOV/ARI details on PCIe devices.
- `virtio_pci_device_unplugged()` stops ioeventfd and unmaps modern regions.

## Legacy Transport Behavior
- Legacy writes to `VIRTIO_PCI_GUEST_FEATURES` negotiate 32-bit features, with `VIRTIO_F_BAD_FEATURE` treated specially.
- Legacy `QUEUE_PFN` writes set queue address or reset the whole virtio-pci device when zero.
- Legacy status writes stop ioeventfd before clearing `DRIVER_OK`, restart it when setting `DRIVER_OK`, reset on status zero, and auto-enable PCI bus mastering for old Linux guest compatibility.
- Legacy device config access is routed through `virtio_config_read/write*`, with target-native config endianness handled explicitly.

## Modern Transport Behavior
- Modern common config reads expose selected device/guest feature words, MSI-X vectors, queue count, status, config generation, selected queue state, queue addresses, and queue reset state.
- Modern common config writes update feature selectors, build 64-bit feature arrays from 32-bit guest feature words, assign MSI-X vectors, update status, configure queue size/rings, enable queues, and reset individual queues.
- Queue notifications are handled by MMIO offset divided by notify multiplier or by optional PIO value.
- `virtio_pci_add_shm_cap()` adds 64-bit shared-memory PCI capabilities for devices that need shared memory windows.

## Interrupts and Acceleration
- `virtio_pci_notify()` uses MSI-X when enabled and falls back to legacy INTx via ISR bit 0.
- MSI-X vector assignment validates against `proxy->nvectors`, marks vectors used/un-used, and coordinates with irqfd if vectors change after `DRIVER_OK`.
- KVM irqfd support builds MSI routes with `accel_irqchip_add_msi_route()`, binds guest notifier eventfds to GSIs, updates routes on unmask, and releases virqs when vectors are unused.
- Guest notifier setup creates event notifiers for queues and config interrupts, configures irqfd/vector notifiers when available, and carefully unwinds on assignment errors.
- ioeventfd assignment registers/removes eventfds for modern MMIO notify, optional modern PIO notify, and legacy notify port.

## Migration and Reset
- Saves PCI state, MSI-X state, config vector, queue vectors, and modern transport state in VMState subsections.
- Modern migration state includes feature selectors, guest feature words, and per-queue modern configuration. A subsection covers feature words beyond the first 64 bits.
- Reset clears virtio bus state, unuses MSI-X vectors, clears negotiated guest features, and zeros modern queue cached configuration.
- Bus reset honors PCIe PM `No_Soft_Reset` while in D3hot.
- VM run/stop transitions start and stop ioeventfd; a migration compatibility flag can re-enable bus mastering for old migrated machines.

## Interfaces Exported
- `virtio_pci_get_trans_devid()`
- `virtio_pci_get_class_id()`
- `virtio_pci_add_shm_cap()`
- `virtio_pci_types_register()`
- `virtio_pci_optimal_num_queues()`

## Filesystem/Storage Relevance
This file is central for all PCI-attached virtio storage devices in this group and elsewhere: block, SCSI, pmem, fs, RNG, serial, and other devices rely on this transport for queue setup, DMA routing, notifications, interrupts, migration, and reset behavior.

## Notable Constraints and Risks
- PCI config capability access uses guest-controlled offsets/lengths and explicitly validates only 1/2/4-byte lengths, aligning offsets before dispatch.
- Legacy and modern mode compatibility checks are critical for migration and machine-type behavior.
- irqfd/MSI-X ordering is delicate: vector notifiers must be unset while guest notifiers still exist and set only after notifier assignment.
- Queue count helpers avoid exceeding MSI-X and `VIRTIO_QUEUE_MAX`, but individual devices still need correct fixed queue accounting.
