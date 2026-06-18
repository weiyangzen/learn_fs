# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibdm/ibdm_ibnex.h

## Scope

Private interface between the InfiniBand Device Manager (IBDM) and the IB nexus driver. It exposes discovery status, HCA/port/IOC/IOU data structures, event callbacks, and query/free routines used by the nexus.

## APIs And Structures

- `ibdm_status_t` returns `IBDM_SUCCESS` or `IBDM_FAILURE`.
- `ibdm_events_t` reports HCA add/remove, IOC property update, port up, and port P_Key change events to IB nexus.
- `ibdm_ibnex_get_ioclist_mtd_t` controls IOC list behavior: normal probe, no probe, or reprobe all.
- `ibdm_timeout_cb_args_t` carries timeout callback context for GID, request type, IOC number, retry count, and service-entry range.
- `ibdm_srvents_info_t` stores service-entry state, attributes, timeout ID, and callback args.
- `ibdm_ioc_info_t` stores IOC controller profile, service entries, GID list, IOU GUID, timeout IDs, diagnostic-code state, previous reprobe data, update payload, and reachable HCA list.
- `ibdm_iou_info_t` stores IOUnitInfo, IOC array, IOU GUID, diagnostic code, and probe progress count.
- `ibdm_pkey_tbl_t`, `ibdm_port_attr_t`, and `ibdm_hca_list_t` describe P_Key/QP mappings, port attributes, and HCA list entries.
- `ibdm_callback_t` is the IB nexus notification function type.

## Functions

- Callback registration: `ibdm_ibnex_register_callback()` and `ibdm_ibnex_unregister_callback()`.
- Port probing/query/free: `ibdm_ibnex_probe_hcaport()`, `ibdm_ibnex_get_port_attrs()`, `ibdm_ibnex_free_port_attr()`.
- IOC probing/list/query/free: `ibdm_ibnex_probe_ioc()`, `ibdm_ibnex_get_ioc_count()`, `ibdm_ibnex_get_ioc_list()`, `ibdm_ibnex_get_ioc_info()`, `ibdm_ibnex_free_ioc_list()`.
- HCA list/query/free: `ibdm_ibnex_get_hca_list()`, `ibdm_ibnex_get_hca_info_by_guid()`, `ibdm_ibnex_free_hca_list()`.
- Maintenance: `ibdm_ibnex_update_pkey_tbls()` and `ibdm_ibnex_port_settle_wait()`.

## Dependencies

- Includes IBTL common types, IBMF client interface, and IB Device Management attributes.
- Uses timeout IDs, IBTF handles, SAA handles, IBMF handles, and property update payload types.

## Risks And Invariants

- Many returned objects are allocated copies and must be freed through the matching `ibdm_ibnex_free_*()` routine.
- Several structures are annotated as serialized by condition variables, not by embedded locks; callers must respect the implementation’s serialization contract.
- IOC reprobe state preserves previous service/GID data and update payload masks, so copy/free paths must retain both current and previous views until consumers finish comparing them.
- Port/HCA reachability affects nexus-visible IOC property updates; stale HCA lists can make devices appear or disappear incorrectly.
