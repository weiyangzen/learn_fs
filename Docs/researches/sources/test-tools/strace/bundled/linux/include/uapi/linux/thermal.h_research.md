# sources/test-tools/strace/bundled/linux/include/uapi/linux/thermal.h

## Purpose

Defines the generic netlink ABI for Linux thermal zones, trips, cooling devices, governors, and thermal events. strace uses it to decode the `thermal` family, commands, attributes, multicast groups, and event ids.

## Important APIs, Types, and Dependencies

The header has no include dependencies. It exports `THERMAL_NAME_LENGTH`, threshold direction flags, `enum thermal_device_mode`, `enum thermal_trip_type`, family name/version/group names, `enum thermal_genl_attr` for IDs, names, temperatures, trip data, cooling-device data, governor, weight, CPU masks, and threshold data, sampling ids, event ids such as thermal zone create/delete/enable/disable/trip/up/down/change/cdev/governor/threshold, and command ids for getting thermal zones, trips, cooling devices, governors, sampling, and threshold add/delete/flush.

## Control Flow, State, and Integration

Runtime flow is generic netlink request/dump and multicast notification. State belongs to thermal zones, trip points, cooling devices, governors, and thresholds in the kernel thermal framework.

## Risks and Test Signals

Risks include stale enum coverage as new thermal events are added, decoding threshold way flags as single values instead of masks, and losing nested trip/cdev attributes. Test signals include generic netlink decode for every command/event, attribute name formatting, and multicast group display.
