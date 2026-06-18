# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/dditypes.h

This header defines fundamental DDI opaque types and small ABI-visible DDI structures. It includes ISA definitions and base types outside assembly.

It declares opaque DMA handles, DMA window and segment handles, DMA cookies, interrupt cookie types, register and interrupt spec handles, soft interrupt IDs, devinfo handles, devmap data handles, device IDs, event cookies, callback IDs, and periodic handles. `ddi_dma_cookie_t` provides a 64-bit DMA address view plus 32-bit address aliases that respect data-model byte order.

Device-id constants enumerate SCSI WWN/serial, fabric, encapsulated, ATA serial, SCSI VPD T10/EUI/NAA, NVMe namespace id/EUI64/NGUID, and max type. It also defines encode-version constants and minor-name wildcard constants for devid lookup.

`ddi_node_state_t` defines the device node lifecycle state sequence from invalid/proto through linked, bound, initialized, probed, attached, and ready. Comments warn that `DS_ATTACHED` and `DS_READY` should generally not be used outside devcfg state model code.

Kernel-only access definitions include `ddi_device_acc_attr_t`, device attribute versions, endian flags, data ordering modes, data-size constants, `ddi_acc_handle_t`, full `ddi_acc_hdl_t`, `peekpoke_ctlops_t`, and access protection mode constants (`DDI_DEFAULT_ACC`, `DDI_FLAGERR_ACC`, `DDI_CAUTIOUS_ACC`).

Research notes:
- This is a low-level type foundation used by many other headers in this group.
- Several types are intentionally opaque to keep public ABI separated from private implementation.
- `ddi_acc_hdl_t` is kernel-private full state for data access mappings and is referenced by mapping and access routines.
