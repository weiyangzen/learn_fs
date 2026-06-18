# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pool_impl.h

## Purpose
Defines private pools driver ioctl commands, exacct catalog IDs, object classes, ioctl payload structures, property metadata, and 32-bit compatibility layouts.

## Main Interfaces
- Ioctl command codes:
  - `POOL_STATUS`, `POOL_STATUSQ`, `POOL_CREATE`, `POOL_DESTROY`, `POOL_QUERY`
  - `POOL_ASSOC`, `POOL_DISSOC`, `POOL_TRANSFER`, `POOL_XTRANSFER`
  - `POOL_PROPGET`, `POOL_PROPPUT`, `POOL_PROPRM`
  - `POOL_BIND`, `POOL_BINDQ`, `POOL_COMMIT`
- Exacct catalog IDs for system, pool, pset, and CPU groups/properties/timestamps.
- Element classes:
  - `pool_elem_class_t`
  - `pool_resource_elem_class_t`
  - `pool_component_elem_class_t`
- Buffer sizing constants:
  - `POOL_IDLIST_SIZE`
  - `POOL_PROPNAME_SIZE`
  - `POOL_PROPBUF_SIZE`
- Ioctl payloads:
  - `pool_status_t`, `pool_create_t`, `pool_destroy_t`, `pool_query_t`
  - `pool_assoc_t`, `pool_dissoc_t`
  - `pool_transfer_t`, `pool_xtransfer_t`
  - `pool_propget_t`, `pool_propgetall_t`
  - `pool_propput_t`, `pool_proprm_t`
  - `pool_bind_t`, `pool_bindq_t`
- 32-bit variants for pointer-bearing payloads.
- Property flags:
  - `PP_READ`, `PP_WRITE`, `PP_RDWR`, `PP_OPTIONAL`, `PP_STORED`, `PP_INIT`, `PP_HIDDEN`
- Kernel property helpers:
  - `pool_property_t`
  - `pool_propput_common()`
  - `pool_proprm_common()`

## Dependencies And Relationships
Includes CPU partition, exacct catalog, and nvpair support. This is lower-level than `pool.h` and represents the devpool ioctl ABI.

## Research Notes
The header uses packing around `pool_transfer_t` on ABIs where 64-bit alignment differs between native and 32-bit callers.
