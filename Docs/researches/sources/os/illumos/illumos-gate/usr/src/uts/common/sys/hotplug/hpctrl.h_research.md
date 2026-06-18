# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotplug/hpctrl.h

## Role

`hpctrl.h` defines the Hot Plug Controller interface for PCI, CompactPCI, PCIe, and system-bus slots, including slot registration, slot operations, events, LED control, slot/card state, and cfgadm private control data.

## Key Interfaces and Data

- `hpc_slot_t` is an opaque slot handle created by the Hot Plug Services framework.
- `hpc_slot_ops_t` is the controller callback vector: connect, disconnect, insert, remove, and control.
- `hpc_slot_info_t` describes slot version, type, flags, and bus-specific slot data for PCI or SBD.
- Slot types include PCI, CompactPCI, SBD, and PCI Express.
- PCI slot capability flags include 64-bit and testing capability.
- Slot flags control auto-enable and `/dev/cfg` device-link creation.
- `HPC_CTRL_*` commands cover LED get/set, slot state, configured/unconfigured notifications, board type, auto-config enable/disable, slot enable/disable, enum enable/disable, and config/unconfig start/failure.
- LED enums identify fault, power, attention, and active LEDs and off/on/blink states.
- Slot states distinguish empty, disconnected, connected, and unknown.
- Board types distinguish unknown, PCI hotplug, CompactPCI non-hot-swap/basic/full/hot-swap.
- `HPC_EVENT_*` bitmasks cover insertion/removal, power, latch, enum, health, configure/unconfigure, blue LED, attention, power fault, and enum processing controls.
- Error returns cover invalid, duplicate/not-registered slot/bus, unsupported, and failed operations.
- Declares slot register/unregister, slot ops allocation/free, event notification, and bus registration query functions.
- Private cfgadm data includes `hpc_control_data`, 32-bit variant, extra control commands for slot/card info, `hpc_card_info_t`, and `hpc_occupant_info_t`.

## Dependencies and Use

The header is the central hotplug controller contract. It is used by platform hotplug drivers, PCI nexus code, and cfgadm plumbing.

## Research Notes

The interface mixes generic hotplug state with PCI-specific details. Later PCIe-specific headers add richer per-controller state, but this remains the common service API.
