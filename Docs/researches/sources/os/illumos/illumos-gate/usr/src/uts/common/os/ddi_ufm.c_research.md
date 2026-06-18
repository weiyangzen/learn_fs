# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_ufm.c

## Role

`ddi_ufm.c` implements the DDI UFM subsystem, which lets drivers expose upgradable firmware/module image information and image-read support to the `ufm(4D)` pseudo driver. It tracks per-device UFM handles, caches UFM reports, dispatches driver UFM ops, and provides helper setters for image and slot metadata.

## Handle Registry and Locking

UFM handles are stored in a global AVL tree keyed by device path. `ufm_lock` serializes tree access. Each `ddi_ufm_handle_t` has its own lock protecting state and cached data.

The documented lock discipline is:
- acquire `ufm_lock` to find a handle;
- acquire the handle lock;
- release `ufm_lock`;
- inspect state, update cache, or call UFM entry points while holding the handle lock.

Only one UFM handle lock should be held at a time.

## Cache Management

`ufm_cache_invalidate()` frees cached images, slots, strings, misc nvlists, the report nvlist, and resets image count/capability state. It expects the handle lock to be held.

`ufm_cache_fill()` populates the cached report lazily. It returns immediately if a report already exists. Otherwise it:
- calls the driver's `ddi_ufm_op_getcaps()`;
- requires `DDI_UFM_CAP_REPORT`;
- gets image count through `ddi_ufm_op_nimages()` or defaults to one image;
- allocates image records;
- calls `ddi_ufm_op_fill_image()` for each image and validates description/slot count;
- allocates slots and calls `ddi_ufm_op_fill_slot()` for each slot;
- asserts non-empty slots have a version;
- builds nested nvlists for images and slots;
- stores the final report in `ufmh_report`.

Any failure invalidates partially built cache state and returns the driver or local error.

## Image Reading

`ufm_read_img()` checks driver capabilities and the presence of `ddi_ufm_op_readimg()`, rejects unsupported reads, detects offset/length overflow, allocates a 1 MiB staging buffer, and loops until the requested length is copied out. Each iteration calls the driver read op and then `ddi_copyout()` to user/kernel ioctl destination according to copy flags. It returns the number of bytes read through `nreadp`.

## Registration and Driver Helpers

`ufm_init()` initializes the AVL tree and mutex during DDI setup.

`ufm_find()` searches by devpath and returns a handle with its lock held.

`ddi_ufm_init()` validates version and required ops, derives the devinfo path, reuses an old handle if the driver instance registered before, otherwise allocates a new one, records ops/arg/version/state, inserts new handles into the AVL tree, and creates a `ddi-ufm-capable` boolean property.

`ddi_ufm_fini()` marks the handle shutting down and invalidates cache. It does not remove the handle from the AVL tree, allowing reuse across unload/suspend scenarios. `ddi_ufm_update()` invalidates the cache and marks the handle ready unless shutdown is in progress.

Setter helpers update image descriptions, slot counts, image/slot misc nvlists, slot versions, attributes, and image sizes, replacing prior allocated data as needed.

## Subset Relevance

Firmware reporting and image reads matter for storage controllers and device management. This file is driver infrastructure rather than filesystem code, but it supports operational visibility for hardware that backs block and filesystem stacks.
