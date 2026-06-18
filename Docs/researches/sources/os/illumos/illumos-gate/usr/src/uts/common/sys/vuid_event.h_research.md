# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vuid_event.h

## Role

`vuid_event.h` defines the Virtual User Input Device event namespace, `Firm_event` wire structure, and ioctls for devices that can emit VUID-formatted input events.

## Key Interfaces

The VUID address space is segmented into 256-code device ranges. Device IDs include ASCII, TOP, ISO, wheel, lightpen, button, dial, SunView, panel, scroll, workstation, and customer-reserved ranges.

Macros compute segment ranges:
- `vuid_first(devid)`
- `vuid_last(devid)`
- `vuid_in_range(devid, id)`

The workstation range contains virtual keyboard and locator codes:
- shift keys and modifier states,
- button events,
- left/right/top/bottom key groups,
- keypad keys,
- mouse button aliases,
- locator delta and absolute axes,
- batching,
- mouse capability-change events,
- absolute mouse type,
- keyboard layout change.

`Firm_event` contains event ID, pair type, pair offset, value, and timestamp. On LP64, the timestamp is `timeval32`; otherwise it is native `timeval`.

Pair types describe how an event updates associated state: none, set, delta, or absolute.

## Ioctls

VUID format ioctls select native byte stream vs `Firm_event` stream. VUID address ioctls set or get the active segment address for a physical input device. x86 variants use different ioctl numbers to avoid VT conflicts.

`Vuid_addr_probe` carries the default base and requested/current address.

## Research Notes

This is a legacy input ABI designed for human input devices and event-state maintenance. It explicitly excludes high-volume data devices. The structure layout and ioctl values are compatibility-sensitive.
