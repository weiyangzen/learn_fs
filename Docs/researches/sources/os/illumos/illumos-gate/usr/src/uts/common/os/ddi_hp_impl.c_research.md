# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_impl.c

## Role

`ddi_hp_impl.c` is the core DDI hotplug framework implementation for illumos. It provides the kernel-side logic behind coordinated hotplug requests from userland `modctl` paths and nexus-driver hotplug callbacks. The file defines the shared state-machine behavior for physical connectors and virtual ports, including state transitions, probing/unprobing, child online/offline, handle lookup, deregistration, and sysevent emission.

The large introductory block documents the Solaris Hotplug Framework architecture, terminology, and connector/port state machine. It places this file between user tools such as `cfgadm(8)`/`hotplug(8)`, `hotplugd`, `modctl`, DDI/NDI hotplug interfaces, nexus `bus_hp_op` implementations, PCIe hotplug support, and I/O subsystem notifications.

## Main Entry Points

- `ddihp_modctl()` implements hotplug `modctl()` operations by resolving the nexus path to a `dev_info_t`, checking `NEXUS_HAS_HP_OP()`, locking the parent before the child to preserve devinfo locking order, resolving connection handles by name, dispatching either direct `bus_hp_op` create-port operations or `DDIHP_CN_OPS()` calls, and translating DDI status codes to errno values.
- `ddihp_cn_getstate()` asks the nexus for current connection state and updates the handle state and last-change timestamp when it changes.
- `ddihp_cn_unregister()` refreshes state, refuses to remove busy connections above offline state, unlinks the handle from `DEVI(dip)->devi_hp_hdlp`, and frees the name and handle.
- `ddihp_cn_name_to_handle()` linearly searches a nexus device's hotplug handle list by connection name.
- `ddihp_connector_ops()` wraps connector operations, adding pre-change cleanup before downgrade, nexus `bus_hp_op` dispatch, and post-change state handling after change-state operations.
- `ddihp_port_ops()` implements virtual-port get-state, change-state, and remove-port operations.
- `ddihp_cn_gen_sysevent()` emits dynamic reconfiguration sysevents with DR AP IDs and either state-change hints or request types.

## Connector State Handling

Connector downgrade from `DDI_HP_CN_STATE_ENABLED` first calls `ddihp_cn_change_children_state(..., B_FALSE)` to offline dependent virtual-port children, runs `devfs_clean()` to avoid devfs references blocking detach, and calls nexus `DDI_HPOP_CN_UNPROBE` to remove children and ports.

Connector upgrade to enabled updates cached state, records the timestamp, calls `DDI_HPOP_CN_PROBE`, and then attempts to online all dependent child devices. If probe fails, it requests a fallback state of `DDI_HP_CN_STATE_POWERED` so userland can retry enabling later. State changes generate DR sysevents through `ddihp_cn_gen_sysevent()`.

`ddihp_cn_change_children_state()` walks all hotplug handles on the nexus, selects virtual ports that depend on the connector's connection number, and online/offline their `cn_child` devinfo nodes. Online failures are logged but do not stop attempts for sibling children; offline failures stop with `DDI_EBUSY`.

## Port State Handling

Virtual ports use a reduced state range from `PORT_EMPTY` through `ONLINE`. `DDI_HPOP_CN_GET_STATE` derives state from `cn_child` and the child devinfo node state:
- no child means empty or present;
- pre-attached node states map to offline;
- `DS_ATTACHED` maps to maintenance;
- `DS_READY` maps to online, unless `ddi_get_devstate()` reports a non-up device.

`ddihp_port_upgrade_state()` advances one state at a time: empty to present through connector change-state, present to offline via read-only probe and `cn_child` capture, and offline/maintenance to online through `ndi_devi_online()`.

`ddihp_port_downgrade_state()` reverses the flow: online/maintenance is offlined with `devfs_clean()` plus `ndi_devi_offline()`, offline is unprobed back to present through connector change-state, and present can return to empty.

## Locking and Error Behavior

All handle list operations assert the nexus devinfo busy lock. Paths that may later lock child and parent devinfo nodes explicitly enter the parent before the child to match the `devcfg.c` lock-ordering theory statement. `ddihp_modctl()` holds and releases the devinfo node obtained by path.

The code distinguishes DDI-level return codes from errno-level userland results. It logs operational failures with `cmn_err()` where device cleanup, probe, attach, detach, sysevent allocation, or sysevent logging fail.

## Subset Relevance

This file is part of the OS device-tree substrate that filesystem and storage stacks rely on during live insertion/removal of controllers, buses, and devices. It is not filesystem code itself, but it controls whether device nodes can be probed, attached, detached, and represented to userland during storage hotplug.
