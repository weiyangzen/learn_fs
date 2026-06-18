# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotplug/pci/pcie_hp.h

## Role

`pcie_hp.h` defines shared PCI/PCIe hotplug property strings, kernel hotplug controller/slot structures, LED state model, controller mode helpers, and common helper prototypes.

## Key Interfaces and Data

- User-visible property names include help, all, fault/power/attention/active LEDs, card type, board type, and slot condition.
- Defines string values for unknown/on/off/blink/default, PCI hotplug, and cfgadm conditions.
- Kernel constants set max slots, command wait timing, DLL state timeout, and post-power-good wait.
- Hotplug type strings distinguish PCIe native, PCIe ACPI, PCIe proprietary, and PCI SHPC.
- Macros get/set `pcie_hp_ctrl_t` from PCIe bus state and test whether PCIe or PCI hotplug is capable/enabled.
- `pcie_hp_ops_t` is the platform/backend operation vector for hardware init/uninit, slot info init/uninit, slot power on/off, and interrupt enable/disable.
- `pcie_hp_occupant_info_t` mirrors occupant string arrays for cfgadm-style reporting.
- `pcie_hp_led_t` and `pcie_hp_led_state_t` define known LED IDs and hardware LED states.
- Newer logical LED management types (`pcie_hp_led_act_t`, `pciehpc_logical_led_t`, `pciehpc_led_plat_id_t`, `pciehpc_led_plat_state_t`) model base, powered, power transition, probe failed, power fault, and attention-button states mapped onto power/attention LEDs.
- `pcie_hp_slot_t` stores logical/physical/device numbers, minor, connector info/state, hardware LED states, user LED overrides, logical LED event state, cfgadm condition, attention-button and DLL condition variables, event kstats, and parent controller.
- `pcie_hp_regops_t` abstracts non-standard hotplug register access.
- `pcie_hp_ctrl_t` stores controller devinfo, mutex, flags, slot array, feature booleans, command completion state, PCIe ops, SHPC bus-speed/device layout, register ops, and backend private data.
- Additional helper structs support configure/unconfigure tree walks, port unregistration, and port state queries.
- Flags track controller initialization and startup synchronization state.
- Declares common init/uninit/intr/probe/unprobe operations, hotplug common ops dispatch, device lookup, occupant property management, nvlist copyin/out, LED/condition text helpers, minor-node management, and sysevent request generation.

## Dependencies and Use

Kernel sections include DDI hotplug and PCIe implementation headers. Non-kernel consumers mainly see property names. Backend-specific headers `pciehpc.h` and `pcishpc.h` use these shared structures.

## Research Notes

This header is both a compatibility bridge and an active design center. Oxide-era additions add a logical LED state machine while preserving shared structures used by both native PCIe and SHPC paths.
