# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp.h

Public DDI hotplug support definitions. It defines hotplug connection states, connection types, connection metadata, dependency numbering, property buffer payloads, and 32-bit property compatibility structure.

Key elements:
- Hotplug connection state enum covers empty, present, powered, enabled, virtual-port empty/present, offline, attached, maintenance, and online states.
- Connection type enum distinguishes virtual ports, PCI slots, and PCI Express slots.
- Defines the type string for virtual ports and `DDI_HP_CN_NUM_NONE` for no same-parent dependency.
- `ddi_hp_cn_info_t` describes a connector or port: name, number, dependency number, type, type string, optional child device for ports, current state, and last-change time.
- `ddi_hp_property_t` carries an nvlist buffer pointer and size for hotplug property get/set operations.
- `_SYSCALL32` block defines `ddi_hp_property32_t` with 32-bit pointer and size fields.

Dependencies:
- Uses `dev_info_t`, `time32_t`, and 32-bit syscall types from surrounding kernel/DDI headers.
- Implemented by DDI hotplug core and bus nexus drivers.

Research notes:
- The state enum uses spaced hex values, making states easy to classify by range and stable for external reporting.
- A connection can be a connector or a port; `cn_child` being non-null identifies the child device only for ports.
