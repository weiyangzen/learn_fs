# File Research: sources/virtualization/spdk/lib/vmd/led.c

## Purpose
Implements SPDK VMD LED state get/set helpers by translating SPDK LED states into PCIe slot attention/power indicator control bits.

## Key Elements
Defines `vmd_led_indicator_config` and a static table mapping `SPDK_VMD_LED_STATE_OFF`, `IDENTIFY`, `FAULT`, and `REBUILD` to attention and power indicator control values. `vmd_led_set_indicator_control` updates the PCIe slot control register and reads it back into `cached_slot_control` to flush posted PCI config writes.

`vmd_led_get_state` compares cached slot-control bits against the known table and returns the matching SPDK state or `SPDK_VMD_LED_STATE_UNKNOWN`.

`vmd_get_led_device` maps an SPDK PCI device to the VMD bridge/slot device that owns the LED. For endpoint devices, it returns the parent type-1 device; for type-1 header devices, it returns the device itself. This supports both occupied endpoint slots and empty slot identification.

Public APIs are `spdk_vmd_set_led_state` and `spdk_vmd_get_led_state`. They validate state or VMD membership, find the LED-bearing VMD device, then set or return the LED state.

## Dependencies
Depends on SPDK stdinc, likely, log, and VMD internals including `vmd_pci_device`, `vmd_find_device`, PCI header type constants, PCIe slot control register layout, and `enum spdk_vmd_led_state`.

## Behavior/Risks
Only four concrete LED states are settable; invalid states return `-EINVAL`. Devices not found behind VMD, endpoints without parents, and non-VMD paths return `-ENODEV`.

State reads use the cached slot-control register, not a fresh config-space read. Correctness therefore depends on cache maintenance by VMD code and by the write helper's posted-write flush.
