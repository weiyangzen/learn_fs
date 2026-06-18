# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/adapters/mpapi_impl.h

## Purpose
Defines the illumos MPAPI kernel/driver ioctl ABI used by multipathing code, especially `scsi_vhci`, to exchange plugin, device-product, logical-unit, path, initiator-port, target-port, target-port-group, and proprietary load-balance properties with MPAPI consumers.

## Main Interfaces
- Shared MPAPI property structures:
  - `mp_driver_prop_t`
  - `mp_vendor_prod_info_t`
  - `mp_dev_prod_prop_t`
  - `mp_logical_unit_prop_t`
  - `mp_init_port_prop_t`
  - `mp_target_port_prop_t`
  - `mp_tpg_prop_t`
  - `mp_path_prop_t`
  - `mp_proprietary_loadbalance_prop_t`
- Command input structures:
  - `mp_lu_tpg_pair_t`
  - `mp_set_tpg_state_req_t`
  - `mp_set_lu_lb_type_req_t`
- SCSI passthrough support:
  - `mp_uscsi_cmd_t` carries `scsi_address`, `uscsi_cmd`, buffers, pathinfo, and auto-request-sense state.
- Ioctl payload headers:
  - `mp_iocdata_t`
  - `mp_iocdata32_t` under `_KERNEL` and `_SYSCALL32`
- Constants for:
  - MP transfer direction (`MP_XFER_*`)
  - object types (`MP_OBJECT_TYPE_*`)
  - ioctl command and subcommands (`MP_CMD`, `MP_GET_*`, `MP_SET_*`, `MP_SEND_SCSI_CMD`)
  - load-balance types, name types, transport types, ALUA access states, path states, and MPAPI driver error values
  - object ID packing/extraction macros
  - sysevent class/subclass strings for plugin, LU, path, initiator, TPG, target-port, and product changes.

## Dependencies And Relationships
Includes `sys/sunmdi.h`, `sys/sunddi.h`, `sys/mdi_impldefs.h`, and `sys/debug.h`. The structures are consumed by MPAPI ioctl handling and by `mpapi_scsi_vhci.h`, which layers `scsi_vhci` object-list state on top of these public-ish property records.

## Research Notes
The file explicitly states that all structures except `mp_iocdata_t` are kept 64-bit aligned so the same layouts can serve 32-bit and 64-bit applications. The `CTASSERT` checks for `mp_driver_prop_t`, `mp_logical_unit_prop_t`, and `mp_proprietary_loadbalance_prop_t` enforce this ABI. Pointer-bearing proprietary buffers are deliberately represented as trailing `caddr_t` fields, with ILP32 padding when needed.

## Notable Risks
- This is ioctl ABI. Field order, padding, enum values, command numbers, and `CTASSERT` sizes must remain stable.
- `mp_iocdata32_t` compatibility depends on packing and 32-bit pointer/size translation matching the native ioctl contract.
- ID helper macros encode major number and instance into a 64-bit object ID; changing the packing would invalidate stale-ID detection and object lookup.
