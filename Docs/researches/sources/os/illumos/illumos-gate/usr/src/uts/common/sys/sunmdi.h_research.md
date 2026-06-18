# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunmdi.h

`sunmdi.h` declares the Multiplexed I/O/MPxIO framework interface. It defines return codes, opaque pathinfo handles, path states, and vHCI class names for SCSI and IB.

Kernel definitions identify MPxIO components as vHCI, pHCI, or client and provide macros to test a devinfo node's component role. `mdi_pathinfo_state_t` carries basic path state, while additional high bits encode transient/user-disabled/driver-disabled state. Separate pathinfo flags mark hidden paths and removed devices.

The API covers device online/offline hotplug notifications, pHCI retirement/unretirement notifications, MDI-aware devinfo locking, vHCI lookup, attach/detach pre/post hooks, path allocation/free/hold/release, state transitions (`online`, `standby`, `fault`, `offline`), path enable/disable, hidden/removed/inserted state, MPxIO power-management operations, bus power hooks, and path walkers for pHCI/client paths.

Pathinfo member accessors expose client and pHCI devinfo nodes, node name, address, state, flags, instance, pathname forms, and OBP pathname controls. Property helpers mirror DDI property operations for pathinfo nodes: update/remove/iterate/lookup typed values and free returned property data.

pHCI/vHCI registration helpers let transport providers register or unregister by class and devinfo. Additional walkers enumerate vHCIs, pHCIs, clients, and pHCI driver lists. This header sits on top of `sunddi.h`/`esunddi.h` and is the multipath storage/device topology layer in this group.
