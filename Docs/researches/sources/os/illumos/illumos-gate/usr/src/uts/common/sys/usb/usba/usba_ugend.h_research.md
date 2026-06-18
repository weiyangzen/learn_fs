# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_ugend.h

## Role

Defines private data structures and macros for the USB generic driver implementation.

## Key Interfaces

- `usb_ugen_hdl_impl_t` stores ugen client handle state, devinfo, minor-node bit masks/shifts/limits, ugen state pointer, and log name.
- Defines devt lookup list/cache entries and a 10-entry cache.
- Defines minor-node sizing and extraction macros for instance, endpoint index, type, config value/index, interface, and alternate setting.
- Defines `ugen_minor_t`, minor-node type constants for device status, endpoint transfer, endpoint status, and whole-device ownership.
- Defines endpoint count, setup packet size, packet-size macro, and interrupt buffer limit.
- `ugen_ep_t` stores endpoint state, standard/extended descriptors, config/interface/alt identifiers, completion/status fields, open flags, buffer limits, pipe handle/policy, mutex/CV, serialization cookie, data/buf pointers, pollhead, and isochronous state.
- Defines endpoint state flags for active/open, interrupt polling, and isochronous polling.
- `ugen_dev_stat_t` tracks device status open state, exported state, wait CV, and pollhead.
- `ugen_power_t` tracks PM states, busy accounting, wakeup, and current power.
- `ugen_state_t` stores instance state, locks, serialization, log handle, client dev data, endpoint array, minor-node table, device status, PM pointer, max bulk transfer size, and cleanup flags.
- Defines ugen-specific unavailable device states and debug masks.

## Risk Notes

This header controls userland-visible generic USB endpoint access. Minor-number encoding, endpoint state flags, poll wakeups, and serialization must stay coherent or ugen can expose the wrong endpoint, race transfers, or misreport hotplug state.
