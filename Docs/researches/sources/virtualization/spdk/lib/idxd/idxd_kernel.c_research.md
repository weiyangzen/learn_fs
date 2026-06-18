# File Research: sources/virtualization/spdk/lib/idxd/idxd_kernel.c

`idxd_kernel.c` implements the optional kernel-backed IDXD implementation using `libaccel_config`. It discovers enabled kernel IDXD devices and user work queues, maps the kernel work-queue portal, and registers an `spdk_idxd_impl` named `kernel`.

The probe path creates an accel-config context, iterates enabled devices, checks PASID/shared-memory compatibility with SPDK IOMMU state, allocates `spdk_kernel_idxd_device`, records device limits, NUMA node, version, PASID state, and scans enabled user work queues. Only dedicated work queues are supported. For the selected WQ it opens `/dev/char/<major>:<minor>`, mmaps a 4 KiB write portal, records total WQ size, derives `chan_per_device`, and records batch size.

Devices with a usable WQ are passed to the attach callback. Devices without a usable WQ are destructed. Destruction unmaps the portal, closes the fd, unreferences the accel-config context, and frees the wrapper.

The backend’s `portal_get_addr()` returns the mmapped portal. Software-error dumping is currently a stub.

Research notes: this backend depends on kernel provisioning of enabled DSA/IAA devices and dedicated user WQs. It rejects IOMMU-enabled systems without PASID/shared-memory support because userspace cannot supply usable IOVA addresses to the kernel work queue.
