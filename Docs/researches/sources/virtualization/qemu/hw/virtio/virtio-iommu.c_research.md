# File Research: sources/virtualization/qemu/hw/virtio/virtio-iommu.c

Implements QEMU's virtio IOMMU device: domain/endpoint management, IOVA mappings, reserved-region reporting, PCI bus address-space integration, fault reporting, migration state, and IOMMU memory-region translation.

Key entry points:
- `virtio_iommu_device_realize()` initializes the virtio device, request/event queues, config ranges, feature bits, mutexes, PCI IOMMU ops, machine-done notifier, and reset hook.
- `virtio_iommu_handle_command()` consumes virtqueue requests and dispatches attach, detach, map, unmap, and probe commands.
- `virtio_iommu_translate()` implements `IOMMUMemoryRegionClass.translate` for DMA translation and fault reporting.
- `virtio_iommu_find_add_as()` implements PCI IOMMU address-space creation and returns per-device address spaces.
- `virtio_iommu_set_iommu_device()` and `virtio_iommu_unset_iommu_device()` integrate host IOMMU devices, host IOVA restrictions, and page-size masks.
- `virtio_iommu_get_config()` / `virtio_iommu_set_config()` expose and update virtio-iommu config, especially runtime bypass mode.
- `iommu_post_load()` reconstructs endpoint links and address-space mode after migration.

Domain and endpoint model:
- `VirtIOIOMMUDomain` stores a domain id, bypass flag, interval-keyed mapping tree, and attached endpoint list.
- `VirtIOIOMMUEndpoint` stores an endpoint id, current domain pointer, associated `IOMMUMemoryRegion`, and list linkage.
- Domains are keyed by integer id in `s->domains`; endpoints are keyed by SID in `s->endpoints`.
- Mapping keys are non-overlapping `VirtIOIOMMUInterval` ranges compared by overlap-aware `interval_cmp()`, so overlapping maps are rejected by lookup before insertion.

Command behavior:
- Attach validates flags, resolves endpoint, detaches from any previous domain, obtains or creates a compatible domain, switches the endpoint address space, and replays existing mappings to IOMMU notifiers.
- Detach validates endpoint/domain association, unmaps notifier state, removes empty domains, and deletes the endpoint record.
- Map validates flags, domain existence, non-bypass domain state, and non-overlap, then inserts a physical mapping and notifies attached endpoints.
- Unmap removes only mappings fully covered by the requested interval; partial overlap returns `VIRTIO_IOMMU_S_RANGE`.
- Probe fills endpoint reserved-memory properties into a fixed `VIOMMU_PROBE_SIZE` buffer.

PCI/IOMMU integration:
- `virtio_iommu_find_add_as()` lazily creates per-BDF `IOMMUDevice` objects with a root memory region containing both bypass and IOMMU subregions.
- `virtio_iommu_switch_address_space()` enables exactly one of bypass or remapping memory regions according to global bypass, endpoint attachment, and domain bypass state.
- `virtio_iommu_switch_address_space_all()` reapplies that choice across all known PCI devices.
- Host IOMMU devices can contribute allowed IOVA ranges; the code stores their inverse as reserved regions and rebuilds the endpoint reserved-region list together with machine-provided reserved regions.

Translation and notification:
- `virtio_iommu_translate()` starts with no permission, checks bypass, endpoint existence, reserved regions, domain attachment, domain bypass, mapping existence, and read/write permissions.
- MSI reserved regions are passed through; reserved memory regions fault.
- Missing endpoints/domains/mappings and permission failures report faults on the event queue via `virtio_iommu_report_fault()`.
- Map/unmap notifier events are split into aligned power-of-two chunks by `virtio_iommu_notify_map_unmap()`.
- Device IOTLB unmap notifier flags are explicitly unsupported.

Configuration and lifecycle:
- Realize validates `aw-bits` in `[32,64]`, derives input range, page size mask from granule mode, domain range, probe size, and supported feature bits.
- `boot-bypass` initializes `config.bypass`; system reset restores it, while ordinary device reset rebuilds domains/endpoints during the reset exit phase.
- Machine init completion freezes the selected granule so later host IOMMU page-size restrictions cannot invalidate it.
- Unrealize destroys hash tables/trees, mutex, virtqueues, reset hooks, and virtio state.

Migration:
- VMState migrates domains, mappings, endpoint lists, domain bypass state, and `config.bypass`.
- `reconstruct_endpoints()` reconnects loaded endpoint records to live IOMMU memory regions and repopulates `s->endpoints`.
- Post-load re-switches all address spaces because enabled memory regions are derived runtime state.

Important invariants:
- A domain id cannot be reused with a different bypass flag.
- Bypass domains cannot accept map/unmap requests.
- Mappings are stored as whole intervals; unmap does not split partially covered mappings.
- Address-space switching must happen after attach/detach and after bypass config changes.
- Host page-size restrictions can only narrow the page-size mask before the granule is frozen.
- Command request and response buffers are size-checked before use; malformed head/tail sizes trigger virtio device errors.

Filesystem/block relevance:
- This file controls DMA address translation for virtio and PCI devices, including virtual storage devices when routed through a virtio IOMMU. Correct mapping and fault behavior is critical for safe virtual block and filesystem I/O isolation.

Notable risks:
- The unmap implementation rejects partial overlaps rather than splitting mappings, which guest drivers must account for.
- Event queue exhaustion drops fault reporting after logging once.
- Host IOMMU alias handling is deliberately limited; pre-existing host reserved ranges cause aliased BDF rejection.
- `virtio_iommu_translate()` uses fault side effects during DMA translation, so missing event buffers can hide repeated guest faults after the first report.
