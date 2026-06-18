# File Research: sources/virtualization/spdk/lib/vfio_user/host/vfio_user_pci.c

This file implements SPDK’s vfio-user PCI host wrapper. It connects to a vfio-user device, maps PCI BAR/config regions, registers SPDK memory for DMA with the remote device, and exposes BAR access helpers.

`spdk_vfio_user_pci_bar_access()` validates a BAR offset/length, performs direct memcpy when the range is inside a mapped sparse mmap region, and falls back to vfio-user region read/write messages when the region is not mmapped. `spdk_vfio_user_get_bar_addr()` returns a direct pointer only if the requested range is inside an mmapped BAR region.

DMA memory tracking uses a TAILQ of `vfio_memory_region`. `vfio_mr_map_notify()` is registered as an SPDK memory-map callback. On unregister, it finds the region, sends vfio-user DMA unmap, removes it from the list, and frees it. On register, it obtains the memory fd and offset with `spdk_mem_get_fd_and_offset()`, records vaddr as IOVA, adds the region, and sends vfio-user DMA map with the fd.

`vfio_device_get_info_cap()` walks a `vfio_region_info` capability chain. `vfio_device_setup_sparse_mmaps()` parses `VFIO_REGION_INFO_CAP_SPARSE_MMAP`, stores sparse ranges, mmaps each supplied fd when present, closes all fds, and records the sparse mmap count. `vfio_device_map_region()` mmaps a whole BAR when sparse mmap setup is unavailable or fails.

`vfio_device_map_bars_and_config_region()` queries each reported PCI region with `VFIO_USER_DEVICE_GET_REGION_INFO`, stores size/offset/flags, and maps regions that advertise `VFIO_REGION_INFO_FLAG_MMAP`. `vfio_device_unmap_bars()` unmaps all mapped regions and clears region state.

`spdk_vfio_user_setup()` allocates a device, initializes the memory-region list, assigns path and generated name, connects and negotiates vfio-user, queries device info, maps BAR/config regions, allocates the SPDK memory map for DMA notifications, and returns the device. `spdk_vfio_user_release()` unmaps BARs, frees the memory map, closes the socket, and frees the device. `spdk_vfio_user_dev_send_request()` exposes the raw request helper for fuzzing.

Important invariants are fd ownership after region queries, mmap lifetime matching release, maximum memory-region limits, and SPDK memory registration callbacks staying consistent with remote DMA mappings.
