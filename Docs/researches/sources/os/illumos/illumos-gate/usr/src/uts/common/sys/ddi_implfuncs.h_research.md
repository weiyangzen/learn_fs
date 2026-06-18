# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_implfuncs.h

This header declares private implementation entry points for the DDI framework. It is included only for kernel implementation code and pulls in OBP, vnode, task, and project/resource-control types.

The declarations cover bus mapping and fault handling (`i_ddi_bus_map`, `i_ddi_apply_range`, `i_ddi_rnumber_to_regspec`, `i_ddi_map_fault`), DMA and device memory allocation (`i_ddi_mem_alloc`, `i_ddi_mem_free`), device access attribute translation to HAT attributes, cache attribute validation, and fault state set/clear routines for access and DMA handles.

It exposes root nexus event helpers, property operation helpers, PROM property integer extraction, Sun bus child initialization/removal, access-handle allocation and initialization, access/DMA fault protection setup, peek/poke trampoline support, boot-device name conversion, and nodeid allocation/free/take routines.

The file also declares device tree and driver-binding helpers: minor name/devt/spectype conversion, property-list duplication/search/refcounting, driver conf load/unload, node state getters/setters, driver detach, binding name update, bulk bind/unbind, pathname-to-devinfo resolution, prom-path to devfs-path conversion, pseudo/hardware node attach, attached-device checks, and PCI dip detection.

Cache and persistence-related declarations include `/etc/devices` cache initialization/read/cleanup, devid cache init/read/cleanup, devid discovery/register/unregister/devt-list conversion, and retire-store persistence operations.

Resource-control hooks are declared for locked memory accounting, and `preroot_walk_block_devices()` supports early filesystem/block-device discovery before root is mounted. Its callback uses `PREROOT_WALK_BLOCK_DEVICES_NEXT` and `PREROOT_WALK_BLOCK_DEVICES_CANCEL`.

Research notes:
- This is a declaration hub for DDI implementation internals rather than a standalone subsystem.
- Functions are mostly `i_ddi_*`, `impl_*`, or `e_*` private interfaces.
- Several routines are boot/autoconfiguration sensitive; callers likely depend on ordering around root nexus initialization and `/etc/devices` cache reads.
