# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_ufm_impl.h

This is the private kernel implementation header for DDI UFM. It includes AVL tree, public UFM definitions, mutex, nvpair, and base types.

It defines `ddi_ufm_state_t` flags for initialized, ready, and shutting-down handle states. Private functions include `ufm_init()` for DDI startup, `ufm_find()` for the `/dev/ufm` driver to locate a registered handle by path, `ufm_cache_fill()` to build cached report state, and `ufm_read_img()` to service firmware image reads with model-aware copy semantics.

Private structures mirror the public report model. `struct ddi_ufm_slot` stores slot number, version string, attributes, image size, and misc nvlist. `struct ddi_ufm_image` stores image number, description, misc nvlist, slot array, and slot count. `struct ddi_ufm_handle` stores lock, device path, ops vector, driver argument, state, version, lazily cached images/count/capabilities/report nvlist, and AVL linkage.

Research notes:
- The handle explicitly separates driver-provided state from lazily cached report state.
- Correct locking around `ufmh_state` and cached report fields is central to avoiding detach/update races.
- This file is implementation-private and should not be consumed by ordinary drivers.
