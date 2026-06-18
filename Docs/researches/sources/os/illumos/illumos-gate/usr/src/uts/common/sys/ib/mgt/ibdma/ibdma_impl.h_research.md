# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdma/ibdma_impl.h

## Scope

Private IBDMA implementation header defining HCA, port, IOC slot, provider handle, and module state structures.

## APIs And Structures

- Constants define MAD size, DM MAD header size, response time, and `IBDMA_MAX_IOC` of 16.
- `ibdma_hdl_impl_t` maps a consumer handle to IOU GUID and IOC slot index.
- `ibdma_ioc_t` represents one IOC slot: in-use flag, slot number, owning HCA pointer, network-order IOC profile, and service-entry pointer.
- `ibdma_port_t` stores per-port IBMF handle, registration info, implementation capabilities, and parent HCA pointer.
- `ibdma_hca_t` stores list linkage, IBT HCA handle, registered consumer handle list, IOU GUID, network-order IOUnitInfo, IOC slot array, port count, and flexible per-port array.
- `ibdma_mod_state_t` stores the IBT client handle, HCA list lock/list, and HCA count.
- `ibdma_ioc_state_t` defines IOC slot states plus `IBDMA_HDL_MAGIC`.
- Static helpers `ibdma_set_ioc_state()` and `ibdma_get_ioc_state()` manipulate IOC state in an HCA slot.

## Dependencies

- Includes IB verbs transport interface, IB DM attributes, and common MAD definitions.
- Uses kernel `list_t`, `list_node_t`, `kmutex_t`, and `krwlock_t`.

## Risks And Invariants

- The HCA list lock is explicitly used instead of per-HCA reference counts to keep HCA objects alive during consumer operations.
- IOC profiles are stored in network order; update and response code must avoid mixing host-order and wire-order fields.
- `ih_iou_rwlock` protects IOUnit and IOC slot state exposed to fabric requests.
- The header has `#ifdef __cpluplus`, likely a typo for `__cplusplus`; this only affects C++ linkage guards.
